# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from threading import Thread

import numpy as np
import qdarkstyle
import datetime
import cv2
import sys

__author__ = "Nick Zanobini"
__version__ = "1.00"
__license__ = "GNU GPLv3"

guiLayout = uic.loadUiType("ThreadingVideoGui.ui")[0]


class VideoThreadClass(QtCore.QThread):

    newFrame = QtCore.pyqtSignal(QtGui.QImage)

    def __init__(self, window_width, window_height, parent=None):
        super(VideoThreadClass, self).__init__(parent)
        # initialize the video camera stream
        self.stream = WebcamVideoStream(src=-1).start()
        # read the first frame from the stream
        self.frame = self.stream.read()
        # initialize the variable used to indicate if the thread should be stopped
        self.stopped = False
        self.window_height = window_height
        self.window_width = window_width

    def run(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                # stop camera thread
                self.stream.stop()
                return

            # read the next frame from the stream
            self.frame = self.stream.read()
            # resize the frame to the size of the window
            img = cv2.resize(self.frame, (self.window_width, self.window_height), interpolation=cv2.INTER_CUBIC)
            # convert the color from cv2 to QImage format
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # get the dimensions of the image
            height, width, bpc = img.shape
            bpl = bpc * width
            # convert image to QImage
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            # emit signal from thread
            self.newFrame.emit(image)

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


class ThreadingVideoGUI(QtWidgets.QWidget, guiLayout):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.initUI()

    def initUI(self):
        self.running = False
        self.setupImgWindows()

        self.startButton.clicked.connect(self.start_clicked)

        self.videoThread = VideoThreadClass(self.window_width, self.window_height)
        self.videoThread.start()
        self.videoThread.newFrame.connect(self.update_frame)

        self.timers = list()
        self.setup_timers()

    def update_frame(self, image):
        # display latest frame from video thread
        self.VidFrame.setImage(image)

    def setupImgWindows(self):
        self.window_width = self.VidFrame.frameSize().width()
        self.window_height = self.VidFrame.frameSize().height()
        self.VidFrameGUI = self.VidFrame
        self.VidFrame = VideoWidget(self.VidFrame)
        self.VidFrame.hide()

    def update_time(self):
        self.currTimeLabel.setText(datetime.datetime.now().strftime('%I:%M:%S %p'))
        self.currDateLabel.setText(datetime.datetime.now().strftime('%d-%b-%Y'))

    def setup_timers(self):
        timer1 = QtCore.QTimer(self)
        timer1.timeout.connect(self.update_time)
        timer1.start(250)

        self.timers.append(timer1)

    def start_clicked(self):
        self.running = not self.running
        if self.running:
            self.startButton.setText('Stop Video')
            self.VidFrame.show()
        else:
            self.startButton.setText('Start Video')
            self.VidFrame.hide()

    def clear_timers(self):
        while self.timers:
            timer = self.timers.pop()
            timer.stop()

    def closeEvent(self, event):
        self.running = False
        self.videoThread.stop()
        if self.timers:
            self.clear_timers()
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


class WebcamVideoStream:
    def __init__(self, src=-1):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
window = ThreadingVideoGUI(None)
window.setWindowTitle('Simple Video GUI')
window.show()
app.exec_()
