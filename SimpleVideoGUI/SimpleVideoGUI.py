# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from threading import Thread

import numpy as np
import datetime
import cv2
import sys

__author__ = "Nick Zanobini"
__version__ = "1.00"
__license__ = "GNU GPLv3"

guiLayout = uic.loadUiType("SimpleVideoGui.ui")[0]


class SimpleVideoGui(QtWidgets.QWidget, guiLayout):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.running = False
        self.binary_toggle = False
        self.video_stream = Webcam(src=0).start()

        self.timers = list()
        self.VidFrameGUI = self.VidFrame
        self.VidFrame = VideoWidget(self.VidFrame)

        self.startButton.clicked.connect(self.start_clicked)
        self.showBinaryButton.clicked.connect(self.binary_clicked)

        self.setup_timers()
        self.startButton.setFocus()

    def update_time(self):
        self.currTimeLabel.setText(datetime.datetime.now().strftime('%I:%M:%S %p'))
        self.currDateLabel.setText(datetime.datetime.now().strftime('%d-%b-%Y'))

    def setup_timers(self):
        timer1 = QtCore.QTimer(self)
        timer1.timeout.connect(self.update_time)
        timer1.start(250)

        timer2 = QtCore.QTimer(self)
        timer2.timeout.connect(self.update_frame)
        timer2.start(1000.0 / 30)

        self.timers.append(timer1)
        self.timers.append(timer2)

    def start_clicked(self):
        self.running = not self.running
        if self.running:
            self.startButton.setText('Stop Video')
            self.VidFrame.show()
        else:
            self.startButton.setText('Start Video')
            self.VidFrame.hide()

    def binary_clicked(self):
        self.binary_toggle = not self.binary_toggle
        if self.binary_toggle:
            self.showBinaryButton.setText('Show Color')
        if not self.binary_toggle:
            self.showBinaryButton.setText('Show Binary')

    def update_frame(self):
        if self.running:
            frame = self.video_stream.read()
            if self.binary_toggle:
                frame = self.clean_img(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_height, frame_width, _ = frame.shape
            frame = QtGui.QImage(frame.data,
                                 frame_width,
                                 frame_height,
                                 frame.strides[0],
                                 QtGui.QImage.Format_RGB888)
            self.VidFrame.setImage(frame)

    def clean_img(self, img):
        height, width, channels = img.shape
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 127, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C)[1]
        kernel = np.ones((5, 5), np.uint8)
        clean = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        clean = cv2.merge((clean, clean, clean))
        return clean

    def clear_timers(self):
        while self.timers:
            timer = self.timers.pop()
            timer.stop()

    def closeEvent(self, event):
        self.running = False
        self.clear_timers()
        self.video_stream.stop()
        self.close()
        sys.exit()


class VideoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(VideoWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()


class Webcam:
    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src)
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False

    def start(self):
        t = Thread(target=self.update)
        t.daemon = True
        t.start()
        return self

    def update(self):
        while True:
            if self.stopped:
                return

            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


app = QtWidgets.QApplication(sys.argv)
window = SimpleVideoGui(None)
window.setWindowTitle('Simple Video GUI')
window.show()
app.exec_()
