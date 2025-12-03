import sys
import cv2
from PyQt6.QtWidgets import QApplication, QDialog, QVBoxLayout, QComboBox, QPushButton, QLabel

class CamSelector(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Select Camera")
        self.idx = None
        layout = QVBoxLayout()
        
        self.combo = QComboBox()
        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                self.combo.addItem(f"Camera {i}", i)
                cap.release()
        
        layout.addWidget(QLabel("Choose Camera Source:"))
        layout.addWidget(self.combo)
        
        btn = QPushButton("Start")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        self.setLayout(layout)
        
    def accept(self):
        if self.combo.count() > 0:
            self.idx = self.combo.currentData()
        super().accept()

def main():
    app = QApplication(sys.argv)
    
    sel = CamSelector()
    if sel.exec():
        if sel.idx is not None:
            from vital_sense.gui.gui_window import MainWindow
            win = MainWindow(sel.idx)
            win.show()
            sys.exit(app.exec())

if __name__ == "__main__":
    main()
