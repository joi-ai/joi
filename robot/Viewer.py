# -*- coding: utf-8 -*-
import os

from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt


class Viewer(object):
    def __init__(self) -> None:
        self.app = QApplication([])
        self.window = MainWindow()
        self.window.setGeometry(150, 150, 400, 300)
        self.display_loading()

    def update_num(self, num):
        label = QLabel(str(num))
        self.window.setCentralWidget(label)

    def add_widget(self, widget):
        self.window.setCentralWidget(widget)

    def _display_gif(self, filepath):
        movie = QMovie(filepath)
        label = QLabel()
        label.setMovie(movie)
        self.window.setCentralWidget(label)
        movie.start()

    def display_loading(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, '../static/loading.gif')
        self._display_gif(image_path)

    def exec_app(self):
        self.window.show()
        self.app.exec()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JOI AI")

        widget = QLabel("JOI AI")
        font = widget.font()
        font.setPointSize(30)
        widget.setFont(font)
        widget.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.setCentralWidget(widget)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
