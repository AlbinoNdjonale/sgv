from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

class Wait(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.setObjectName("wait")
        
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.update_point)
        
        self.count = 0
        
        self.resize(150, 50)
        
        self.setLayout(QHBoxLayout())
        
        self.points: list[QWidget] = []
        
        for _ in range(7):
            point = QWidget()
            point.setProperty("class", "point")
            point.setStyleSheet("background: lightblue;")
            
            point.setFixedSize(30, 30)
            
            self.layout().addWidget(point)
            
            self.points.append(point)
            
    def update_point(self):
        current_point = self.points[self.count]
        last_point    = self.points[self.count-1]
        
        current_point.setStyleSheet("background: darkblue;")
        last_point.setStyleSheet("background: lightblue;")
        
        self.count += 1
        if self.count == len(self.points):
            self.count = 0
            
    def show(self):
        super().show()
        
        self.timer.start()
        
    def hide(self):
        super().hide()
        
        self.timer.stop()
        