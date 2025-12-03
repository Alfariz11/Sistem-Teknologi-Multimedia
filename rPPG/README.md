# Laporan Tugas: Implementasi Sistem rPPG Berbasis Algoritma POS

**Data Mahasiswa:**
*   **Nama:** Rizki Alfariz Ramadhan
*   **NIM:** 122140061
*   **Program Studi:** Teknik Informatika
*   **Repository:** [GitHub Link](https://github.com/Alfariz11/Sistem-Teknologi-Multimedia/tree/main/rPPG)

---
## 1. Penjelasan

Tugas ini bertujuan untuk mengembangkan sistem *Remote Photoplethysmography* (rPPG) dengan menggunakan metode *Plane-Orthogonal-to-Skin* (POS) dibandingkan metode konvensional berbasis kanal hijau (Green Channel). Sistem yang dikembangkan mengimplementasikan algoritma POS dengan deteksi *Multi-Region of Interest* (ROI) untuk meningkatkan akurasi estimasi detak jantung dalam kondisi pencahayaan yang dinamis.

Metode rPPG tradisional (Verkruysse, 2008) bekerja dengan memantau perubahan intensitas pada kanal warna hijau. Meskipun sederhana, metode ini sangat rentan terhadap *noise* akibat gerakan dan perubahan cahaya. Proyek ini menggunakan pendekatan yang lebih baik menggunakan algoritma POS dengan deteksi Multi-ROI.

## 2. Alur Implementasi
Sistem ini dibangun menggunakan Python. Tahapan pemrosesan sinyal meliputi:
1.  **Akuisisi Citra:** Pengambilan video real-time dari webcam.
2.  **Deteksi Wajah & ROI:** Menggunakan MediaPipe untuk mendeteksi wajah dan menentukan area Dahi serta Pipi.
3.  **Ekstraksi Sinyal:** Mengambil rata-rata nilai piksel RGB dari setiap ROI.
4.  **Algoritma POS:** Memproyeksikan sinyal RGB ke bidang ortogonal untuk memisahkan sinyal darah dari noise.
5.  **Filtering:** Penerapan *Sliding Average Detrending* dan *Bandpass Filter* (0.67-4.0 Hz).
6.  **Estimasi BPM:** Analisis spektral menggunakan FFT (Welch's Method) dan deteksi puncak (*Find Peaks*).

## 3. Implementasi dan Pembahasan

### 3.1. Struktur Sistem
Sistem diorganisir dalam struktur sebagai berikut:

```
rPPG/
├── launcher.py                 # Program utama (Entry Point)
├── requirements.txt            # Daftar pustaka yang dibutuhkan
└── vital_sense/                # Paket Utama
    ├── core/                   # Utilitas dasar
    │   └── utils.py            # Penghitung FPS
    ├── gui/                    # Antarmuka Pengguna
    │   ├── gui_window.py       # Jendela utama aplikasi
    │   └── styles.py           # Definisi tema dan gaya
    ├── logic/                  # Logika Pemrosesan Sinyal
    │   └── processor.py        # Implementasi POS, Filter, FFT
    └── workers/                # Threading & Multitasking
        └── workers.py          # Thread Kamera, Deteksi Wajah, Kalkulasi
```

### 3.2. Algoritma POS (Plane-Orthogonal-to-Skin)
Berbeda dengan metode GREEN yang hanya mengambil rata-rata kanal hijau, POS memproyeksikan sinyal RGB ke bidang ortogonal untuk menghilangkan noise specular (pantulan cahaya).

```python
# vital_sense/logic/processor.py

# 1. Normalisasi Temporal
means = np.mean(sig, axis=0)
norm = sig / means - 1
r, g, b = norm[:, 0], norm[:, 1], norm[:, 2]

# 2. Proyeksi POS (Memisahkan sinyal krominan)
s1 = g - b
s2 = g + b - 2*r

# 3. Penggabungan dengan Tuning Alpha
alpha = np.std(s1) / (np.std(s2) + 1e-6)
h = s1 + alpha * s2
```

### 3.3. Multi-ROI & Weighted Averaging
Saya tidak hanya mengambil satu kotak di wajah, tetapi mendeteksi area spesifik yang kaya pembuluh darah (Dahi dan Pipi) dan memberikan bobot lebih besar pada dahi.

```python
# vital_sense/workers/workers.py

# Ekstrak sinyal dari 3 area berbeda
sig_forehead = self._extract_roi_signal(frame_rgb, fh_x, fh_y, fh_w, fh_h)
sig_right = self._extract_roi_signal(frame_rgb, rc_x, rc_y, ch_w, ch_h)
sig_left = self._extract_roi_signal(frame_rgb, lc_x, lc_y, ch_w, ch_h)

# Weighted Averaging (Dahi 50%, Pipi 25% masing-masing)
# ... (kode penggabungan sinyal)
```

### 3.4. Signal Processing
Saya menerapkan teknik pembersihan sinyal bertingkat untuk hasil yang stabil.

**Sliding Average Detrending & Bandpass Filter:**
Menghilangkan *trend* frekuensi rendah dan membatasi frekuensi pada rentang detak jantung manusia.

```python
# vital_sense/logic/processor.py

# Detrending (Sliding Average Removal)
w_size = int(fs) # Jendela 1 detik
trend = np.convolve(h, np.ones(w_size)/w_size, mode='same')
h = h - trend

# Bandpass Filter (0.67 Hz - 4.0 Hz)
b_filt, a_filt = sg.butter(3, [low, high], btype='band')
filtered = sg.filtfilt(b_filt, a_filt, h)
```

### 3.5. Dynamic Quality Metric
Kualitas sinyal diukur menggunakan **Logarithmic SNR (dB)**, memberikan indikator dinamis 0-100% berdasarkan kejernihan puncak frekuensi detak jantung terhadap *noise floor*.

---

## Lampiran: Instalasi dan Penggunaan

1.  **Install Dependensi:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Jalankan Aplikasi:**
    ```bash
    python launcher.py
    ```
