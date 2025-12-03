import cv2
import mediapipe as mp
import threading
import time
import numpy as np
import queue
from PyQt6.QtCore import pyqtSignal, QObject

class AppSignals(QObject):
    data_update = pyqtSignal(float, bool, float) # BPM, Valid, Quality
    wave_update = pyqtSignal(float)
    face_status = pyqtSignal(bool)

class CamWorker(threading.Thread):
    def __init__(self, idx, q_out):
        super().__init__()
        self.idx = idx
        self.q_out = q_out
        self.active = False

    def run(self):
        cap = cv2.VideoCapture(self.idx, cv2.CAP_DSHOW)
        if not cap.isOpened(): cap = cv2.VideoCapture(self.idx)
        if not cap.isOpened(): return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.active = True
        while self.active:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            ts = time.time()
            if self.q_out.full():
                try: self.q_out.get_nowait()
                except: pass
            self.q_out.put((frame, ts))
            
        cap.release()

    def stop(self):
        self.active = False

class LogicWorker(threading.Thread):
    def __init__(self, q_in, q_sig, q_disp, signals):
        super().__init__()
        self.q_in = q_in
        self.q_sig = q_sig
        self.q_disp = q_disp
        self.signals = signals
        self.active = False
        self.detector = mp.solutions.face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.7)
            
        # Smoothing for bounding box
        self.prev_box = None # [x, y, w, h]
        self.alpha = 0.6 # Smoothing factor (lower = smoother)

    def get_roi_avg(self, img, x, y, w, h):
        H, W, _ = img.shape
        x, y = max(0, x), max(0, y)
        w, h = min(w, W-x), min(h, H-y)
        if w <= 0 or h <= 0: return None
        crop = img[y:y+h, x:x+w]
        return np.mean(crop, axis=(0, 1))

    def run(self):
        self.active = True
        while self.active:
            try:
                item = self.q_in.get(timeout=1.0)
            except: continue
            
            frame_bgr, ts = item
            if frame_bgr is None: continue
            
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            res = self.detector.process(frame_rgb)
            
            disp = cv2.flip(frame_rgb, 1) # Display in RGB
            dh, dw, _ = disp.shape
            
            detected = False
            
            if res.detections:
                detected = True
                det = res.detections[0]
                box = det.location_data.relative_bounding_box
                
                ih, iw, _ = frame_rgb.shape
                bx = int(box.xmin * iw)
                by = int(box.ymin * ih)
                bw = int(box.width * iw)
                bh = int(box.height * ih)
                
                # Smooth BBox
                curr_box = np.array([bx, by, bw, bh], dtype=float)
                if self.prev_box is None:
                    self.prev_box = curr_box
                else:
                    self.prev_box = self.alpha * curr_box + (1 - self.alpha) * self.prev_box
                
                sbx, sby, sbw, sbh = self.prev_box.astype(int)
                
                # ROI Logic (Using smoothed coords)
                fh_w = int(sbw * 0.35)
                fh_h = int(sbh * 0.10)
                fh_x = sbx + (sbw - fh_w) // 2
                fh_y = sby + int(sbh * 0.02) 
                
                ch_w = int(sbw * 0.10)
                ch_h = int(sbh * 0.12)
                
                rc_x = sbx + int(sbw * 0.20)
                rc_y = sby + int(sbh * 0.45)
                
                lc_x = sbx + int(sbw * 0.70)
                lc_y = sby + int(sbh * 0.45)
                
                s1 = self.get_roi_avg(frame_rgb, fh_x, fh_y, fh_w, fh_h)
                s2 = self.get_roi_avg(frame_rgb, rc_x, rc_y, ch_w, ch_h)
                s3 = self.get_roi_avg(frame_rgb, lc_x, lc_y, ch_w, ch_h)
                
                vals = [x for x in [s1, s2, s3] if x is not None]
                if vals:
                    avg = np.mean(vals, axis=0)
                    self.q_sig.put((avg, ts))
                    self.signals.wave_update.emit(avg[1])
                
                # Draw (Flipped)
                def draw(x, y, w, h, c):
                    fx = dw - (x + w)
                    cv2.rectangle(disp, (fx, y), (fx+w, y+h), c, 2)
                    
                draw(sbx, sby, sbw, sbh, (255, 255, 255))
                draw(fh_x, fh_y, fh_w, fh_h, (0, 255, 0))
                draw(rc_x, rc_y, ch_w, ch_h, (255, 255, 0))
                draw(lc_x, lc_y, ch_w, ch_h, (255, 255, 0))
            else:
                self.prev_box = None
                
            self.signals.face_status.emit(detected)
            
            if self.q_disp.full():
                try: self.q_disp.get_nowait()
                except: pass
            self.q_disp.put(disp)

    def stop(self):
        self.active = False

class CalcWorker(threading.Thread):
    def __init__(self, q_sig, signals):
        super().__init__()
        self.q_sig = q_sig
        self.signals = signals
        self.active = False
        self.buf_val = []
        self.buf_ts = []
        
    def run(self):
        from vital_sense.logic.processor import PulseProcessor
        proc = PulseProcessor()
        self.active = True
        
        while self.active:
            try:
                val, ts = self.q_sig.get(timeout=1.0)
            except: continue
            
            self.buf_val.append(val)
            self.buf_ts.append(ts)
            
            if len(self.buf_val) > 150:
                self.buf_val.pop(0)
                self.buf_ts.pop(0)
                
            if len(self.buf_val) >= 90 and len(self.buf_val) % 5 == 0:
                bpm, valid, qual = proc.compute(self.buf_val, self.buf_ts)
                
                # Quality Threshold
                is_ok = bpm is not None and 45 <= bpm <= 200 and qual > 5
                self.signals.data_update.emit(bpm if is_ok else 0.0, is_ok, qual)
                
    def stop(self):
        self.active = False
