import numpy as np
from scipy import signal as sg

class PulseProcessor:
    """Core logic for extracting heart rate from RGB signals."""
    def __init__(self):
        self.history = []
        self.max_hist = 15
        self.last_bpm = None
        
    def compute(self, rgb_data, timestamps):
        """
        rgb_data: list of (R, G, B) tuples
        timestamps: list of floats
        """
        if len(rgb_data) < 90: return None, 0.0, 0.0 # Need ~3s data
        
        # 1. Pre-processing
        sig = np.array(rgb_data)
        
        # Moving Average Smoothing (Noise Reduction)
        for i in range(3):
            sig[:, i] = np.convolve(sig[:, i], np.ones(5)/5, mode='same')
            
        # 2. POS Algorithm
        means = np.mean(sig, axis=0)
        norm = sig / means - 1
        
        r, g, b = norm[:, 0], norm[:, 1], norm[:, 2]
        
        s1 = g - b
        s2 = g + b - 2*r
        
        alpha = np.std(s1) / (np.std(s2) + 1e-6)
        h = s1 + alpha * s2
        
        # 3. Filtering
        dt = timestamps[-1] - timestamps[0]
        fs = len(rgb_data) / dt
        
        # Detrending (Sliding Average Removal)
        w_size = int(fs) # 1 second window
        if w_size > 0:
            trend = np.convolve(h, np.ones(w_size)/w_size, mode='same')
            h = h - trend
        
        # Bandpass Filter (0.67 Hz - 4.0 Hz)
        nyq = 0.5 * fs
        low = 0.67 / nyq
        high = 4.0 / nyq
        
        if low <= 0: low = 0.01
        if high >= 1: high = 0.99
            
        b_filt, a_filt = sg.butter(3, [low, high], btype='band')
        filtered = sg.filtfilt(b_filt, a_filt, h)
        
        # 4. FFT with FindPeaks
        n_fft = max(len(filtered) * 4, 2048)
        freqs, psd = sg.welch(filtered, fs, nperseg=len(filtered), nfft=n_fft)
        
        # Mask for valid HR range (0.67 - 4.0 Hz)
        mask = (freqs >= 0.67) & (freqs <= 4.0)
        valid_f = freqs[mask]
        valid_p = psd[mask]
        
        if len(valid_p) == 0: return None, 0.0, 0.0
        
        # Use find_peaks to find local maxima
        peaks, _ = sg.find_peaks(valid_p, height=np.max(valid_p)*0.3)
        
        if len(peaks) > 0:
            peak_idx = peaks[np.argmax(valid_p[peaks])]
        else:
            peak_idx = np.argmax(valid_p)
            
        bpm = valid_f[peak_idx] * 60.0
        
        # SNR 
        # Signal Power: Power around the peak (+/- 0.15 Hz)
        bin_width = valid_f[1] - valid_f[0]
        half_width = int(0.15 / bin_width)
        
        start = max(0, peak_idx - half_width)
        end = min(len(valid_p), peak_idx + half_width + 1)
        
        signal_power = np.sum(valid_p[start:end])
        total_power = np.sum(valid_p)
        noise_power = total_power - signal_power
        
        if noise_power <= 0:
            snr_db = 20.0 
        else:
            snr_db = 10 * np.log10(signal_power / noise_power)
            
        # -5 dB -> 0% (Very noisy)
        # 10 dB -> 100% (Very clean)
        quality = (snr_db + 5) * (100 / 15)
        quality = min(100, max(0, quality))
            
        # 5. Post-smoothing
        if self.last_bpm is not None:
            diff = abs(bpm - self.last_bpm)
            if diff > 12: 
                bpm = 0.2 * bpm + 0.8 * self.last_bpm
            else:
                bpm = 0.6 * bpm + 0.4 * self.last_bpm
                
        self.history.append(bpm)
        if len(self.history) > self.max_hist: self.history.pop(0)
        
        final_bpm = np.median(self.history)
        self.last_bpm = final_bpm
        
        return final_bpm, 1.0, quality
