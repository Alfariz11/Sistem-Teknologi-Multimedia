import cv2
import queue
from PyQt6 import QtWidgets, QtCore, QtGui
from vital_sense.gui.styles import AppStyles, AppColors, get_status_color
from vital_sense.workers.workers import CamWorker, LogicWorker, CalcWorker, AppSignals
from vital_sense.core.utils import FPSCounter


# Re-implementing PlotCanvas here to avoid dependency on old folder or move it
import matplotlib
matplotlib.use('QtAgg')
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class SimpleGraph(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 3), dpi=100)
        self.fig.patch.set_facecolor(AppColors.PANEL_BG)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(AppColors.PANEL_BG)
        self.line, = self.ax.plot([], [], color=AppColors.ACCENT, lw=1.5)
        self.ax.axis('off') # Minimalist
        self.fig.tight_layout(pad=0)

    def update_data(self, data):
        if len(data) < 2: return
        y = np.array(data)
        x = np.arange(len(y))
        self.line.set_data(x, y)
        self.ax.set_xlim(0, len(y))
        mi, ma = np.min(y), np.max(y)
        d = (ma - mi) * 0.1
        if d == 0: d = 1
        self.ax.set_ylim(mi-d, ma+d)
        self.draw_idle()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, cam_idx=0):
        super().__init__()
        self.setWindowTitle("Vital Sense")
        self.resize(1000, 600)
        self.setStyleSheet(AppStyles.MAIN)
        
        self.cam_idx = cam_idx
        self.init_ui()
        self.init_logic()
        
    def init_ui(self):
        main = QtWidgets.QWidget()
        self.setCentralWidget(main)
        layout = QtWidgets.QHBoxLayout(main)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left: Video
        vid_panel = QtWidgets.QWidget()
        vid_layout = QtWidgets.QVBoxLayout(vid_panel)
        
        self.lbl_vid = QtWidgets.QLabel()
        self.lbl_vid.setMinimumSize(640, 480)
        self.lbl_vid.setStyleSheet(f"background-color: #000; border: 2px solid {AppColors.BORDER}; border-radius: 8px;")
        self.lbl_vid.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        vid_layout.addWidget(self.lbl_vid)
        
        # Info
        info = QtWidgets.QHBoxLayout()
        self.lbl_fps = QtWidgets.QLabel("FPS: 0")
        self.lbl_fps.setStyleSheet(f"color: {AppColors.TEXT_DIM};")
        info.addWidget(self.lbl_fps)
        info.addStretch()
        vid_layout.addLayout(info)
        
        layout.addWidget(vid_panel)
        
        # Right: Stats
        stats_panel = QtWidgets.QWidget()
        stats_panel.setStyleSheet(AppStyles.PANEL)
        stats_layout = QtWidgets.QVBoxLayout(stats_panel)
        stats_layout.setSpacing(30)
        
        # Title
        lbl_title = QtWidgets.QLabel("HEART RATE")
        lbl_title.setStyleSheet(AppStyles.TITLE)
        lbl_title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(lbl_title)
        
        # BPM
        self.lbl_bpm = QtWidgets.QLabel("--")
        self.lbl_bpm.setStyleSheet(f"font-size: 80px; font-weight: bold; color: {AppColors.TEXT_MAIN};")
        self.lbl_bpm.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(self.lbl_bpm)
        
        self.lbl_status = QtWidgets.QLabel("Initializing...")
        self.lbl_status.setStyleSheet(f"font-size: 16px; color: {AppColors.TEXT_DIM};")
        self.lbl_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        stats_layout.addWidget(self.lbl_status)
        
        # Graph
        self.graph = SimpleGraph()
        stats_layout.addWidget(self.graph)
        
        stats_layout.addStretch()
        layout.addWidget(stats_panel)
        
    def init_logic(self):
        self.q_frame = queue.Queue(maxsize=2)
        self.q_sig = queue.Queue(maxsize=100)
        self.q_disp = queue.Queue(maxsize=2)
        
        self.signals = AppSignals()
        self.signals.data_update.connect(self.on_data)
        self.signals.wave_update.connect(self.on_wave)
        self.signals.face_status.connect(self.on_face)
        
        self.w_cam = CamWorker(self.cam_idx, self.q_frame)
        self.w_logic = LogicWorker(self.q_frame, self.q_sig, self.q_disp, self.signals)
        self.w_calc = CalcWorker(self.q_sig, self.signals)
        
        self.w_cam.start()
        self.w_logic.start()
        self.w_calc.start()
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(30)
        
        self.fps = FPSCounter()
        self.wave_data = []

    def update_gui(self):
        if not self.q_disp.empty():
            frame = self.q_disp.get()
            self.fps.update()
            self.lbl_fps.setText(f"FPS: {self.fps.get_fps():.1f}")
            
            h, w, c = frame.shape
            img = QtGui.QImage(frame.data, w, h, c*w, QtGui.QImage.Format.Format_RGB888)
            self.lbl_vid.setPixmap(QtGui.QPixmap.fromImage(img.scaled(640, 480, QtCore.Qt.AspectRatioMode.KeepAspectRatio)))
            
        if len(self.wave_data) > 0:
            self.graph.update_data(self.wave_data)

    def on_data(self, bpm, valid, qual):
        if valid:
            self.lbl_bpm.setText(str(int(bpm)))
            c = get_status_color(bpm)
            self.lbl_bpm.setStyleSheet(f"font-size: 80px; font-weight: bold; color: {c};")
            self.lbl_status.setText(f"Quality: {int(qual)}%")
        else:
            self.lbl_bpm.setText("--")
            self.lbl_bpm.setStyleSheet(f"font-size: 80px; font-weight: bold; color: {AppColors.TEXT_DIM};")
            self.lbl_status.setText("Measuring...")

    def on_wave(self, val):
        self.wave_data.append(val)
        if len(self.wave_data) > 100: self.wave_data.pop(0)

    def on_face(self, detected):
        if not detected:
            self.lbl_status.setText("No Face Detected")
            self.lbl_status.setStyleSheet(f"color: {AppColors.STATUS_BAD}; font-size: 16px;")

    def closeEvent(self, event):
        self.w_cam.stop()
        self.w_logic.stop()
        self.w_calc.stop()
        event.accept()
