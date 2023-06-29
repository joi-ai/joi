# -*- coding: utf-8 -*-
import os
import sys
from robot import logging
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QStackedLayout, QVBoxLayout
from PyQt5.QtGui import QMovie, QColor, QPalette
from PyQt5.QtMultimedia import QMediaPlaylist, QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from . import config

logger = logging.getLogger(__name__)


class Viewer():
    def __init__(self, parent):
        self.app = QApplication([])
        self.player = Player()
        self.thread = parent.detector_thread
        self.thread.signal.connect(self.update_video_url)

    def update_video_url(self, url):
        self.player.play_video(url)

    def exec_app(self):
        self.player.show()
        # self.player.showFullScreen()
        self.app.exec()


class Player(QMainWindow):
    def __init__(self):
        super().__init__()

        desktop = QApplication.desktop()
        width = config.get('/screen/width', desktop.width())
        height = config.get('/screen/height', desktop.height())

        self.setWindowTitle("Video Player")
        self.setGeometry(0, 0, width, height)

        # 视频播放控件
        self.video_widget = QVideoWidget(self)
        self.loop_video_widget = QVideoWidget(self)
        self.player = QMediaPlayer()
        self.loop_player = QMediaPlayer()
        self.loop_playlist = QMediaPlaylist()
        self.loop_playlist.setPlaybackMode(QMediaPlaylist.Loop)

        # 两个视频组件，z-index 0 用于播放问答视频，z-index 1 用于播放 idle 视频循环播放
        self.player.setVideoOutput(self.video_widget)
        self.player.mediaStatusChanged.connect(self.on_player_status_changed)
        self.loop_player.setVideoOutput(self.loop_video_widget)

        # gif 动图播放控件参数 z-index 3
        self.gif_label = QLabel()
        self.gif_label.setAlignment(Qt.AlignCenter)
        self.gif_label.setScaledContents(True)
        self.gif_label.setFixedSize(width, height)
        self.gif = QMovie()
        self.gif_label.setMovie(self.gif)

        self.layout = QStackedLayout()
        self.layout.addWidget(self.video_widget)
        self.layout.addWidget(self.loop_video_widget)
        self.layout.addWidget(self.gif_label)

        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: black;")
        self.setCentralWidget(central_widget)
        central_widget.setLayout(self.layout)

    # 动图组件方法

    def set_gif_path(self, path):
        self.gif_path = path

    def play_gif(self, path):
        self.set_gif_path(path)
        self.layout.setCurrentIndex(2)
        self.gif = QMovie(path)
        self.gif_label.setMovie(self.gif)
        self.gif.start()

    def play_loading(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, '../static/loading.gif')
        self.play_gif(image_path)

    def show_entry(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, '../static/sphere.gif')
        self.play_gif(image_path)

    def play_idle(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(current_dir, '../static/idle.mp4')
        self.loop_playlist.addMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.loop_player.setPlaylist(self.loop_playlist)
        self.loop_player.play()
        self.layout.setCurrentIndex(1)

    # 视频组件方法

    def set_video_url(self, url):
        self.video_url = url

    def play_video(self, url):
        self.set_video_url(url)
        content = QMediaContent(QUrl.fromUserInput(url))
        self.player.setMedia(content)
        self.player.play()
        self.layout.setCurrentIndex(0)

    def play(self):
        self.player.play()

    def stop(self):
        self.player.stop()

    def pause(self):
        self.pause()

    def on_player_status_changed(self, status):
        # print('on_player_status_changed', status)
        # status 2: start loading, 4 loaded, 6 loading, 7 end
        if status == 7:
            self.play_idle()
        if status == 4:
            self.layout.setCurrentIndex(0)

    def on_player_error(self):
        palette = self.video_widget.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        self.video_widget.setPalette(palette)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.player.stop()
