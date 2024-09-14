from PyQt6.QtWidgets import QApplication
import sys

from base_path import base_path

app = QApplication(sys.argv)
with open(base_path+"/style/style.qss") as style:
    app.setStyleSheet(style.read())