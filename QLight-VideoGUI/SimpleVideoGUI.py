# -*- coding: utf-8 -*-
import subprocess
import os

path = dir_path = os.path.dirname(os.path.realpath(__file__))
convert_UI_cmd = 'pyuic5 -x ' + path + os.sep  + 'SimpleVideoGUI.ui ' '-o ' + path + os.sep + 'UI_SimpleVideoGUI.py'

_, _ = subprocess.getstatusoutput(convert_UI_cmd)

from PyQt5 import QtCore, QtGui, QtWidgets
from UI_SimpleVideoGUI import Ui_SimpleVideoGUI
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread

import numpy as np
import qdarkstyle
import datetime
import cv2
import sys

__author__ = "Nick Zanobini"
__version__ = "1.00"
__license__ = "GNU GPLv3"

# guiLayout = uic.loadUiType("SimpleVideoGui.ui")[0]
qlight_path = os.path.join(path, 'qlight')
green_on = 'sudo ' + qlight_path + ' -g on'
green_blink = 'sudo ' + qlight_path + ' -g blink'
green_off = 'sudo ' + qlight_path + ' -g off'
yellow_on = 'sudo ' + qlight_path + ' -y on'
yellow_blink = 'sudo ' + qlight_path + ' -y blink'
yellow_off = 'sudo ' + qlight_path + ' -y off'
red_on = 'sudo ' + qlight_path + ' -r on'
red_blink = 'sudo ' + qlight_path + ' -r blink'
red_off = 'sudo ' + qlight_path + ' -r off'


class SimpleVideoGui(QtWidgets.QWidget, Ui_SimpleVideoGUI):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.callning = False
        self.video_stream = Webcam(src=0).start()

        self.redStatus = 'off'
        _, _ = subprocess.getstatusoutput(red_off)
        self.yellowStatus = 'off'
        _, _ = subprocess.getstatusoutput(yellow_off)
        self.greenStatus = 'off'
        _, _ = subprocess.getstatusoutput(green_off)

        self.timers = list()
        self.VidFrameGUI = self.VidFrame
        self.VidFrame = VideoWidget(self.VidFrame)

        self.startButton.clicked.connect(self.start_clicked)
        self.restartButton.clicked.connect(self.restart_clicked)
        self.redLightButton.clicked.connect(self.red_clicked)
        self.yellowLightButton.clicked.connect(self.yellow_clicked)
        self.greenLightButton.clicked.connect(self.green_clicked)
        self.redBlinkButton.clicked.connect(self.red_blink_clicked)
        self.yellowBlinkButton.clicked.connect(self.yellow_blink_clicked)
        self.greenBlinkButton.clicked.connect(self.green_blink_clicked)

        self.setup_timers()

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
        self.startButton.clearFocus()
        self.callning = not self.callning
        if self.callning:
            self.startButton.setText('Stop Video')
            self.VidFrame.show()
        else:
            self.startButton.setText('Start Video')
            self.VidFrame.hide()

    def restart_clicked(self):
        command = "/usr/bin/sudo /sbin/reboot"
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        _ = process.communicate()[0]

    def update_frame(self):
        if self.callning:
            frame = self.video_stream.read()
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_height, frame_width, _ = frame.shape
            frame = QtGui.QImage(frame.data,
                                 frame_width,
                                 frame_height,
                                 frame.strides[0],
                                 QtGui.QImage.Format_RGB888)
            self.VidFrame.setImage(frame)

    def clear_timers(self):
        while self.timers:
            timer = self.timers.pop()
            timer.stop()

    def closeEvent(self, event):
        self.callning = False
        self.clear_timers()
        self.video_stream.stop()
        self.close()
        sys.exit()

    def red_clicked(self):
        self.redLightButton.clearFocus()
        if self.redStatus == 'off':
            self.redStatus = 'on'
            _, _ = subprocess.getstatusoutput(red_on)
            self.redLightButton.setText('Red Off')
        elif self.redStatus == 'on':
            self.redStatus = 'off'
            _, _ = subprocess.getstatusoutput(red_off)
            self.redLightButton.setText('Red On')
        elif self.redStatus == 'blink':
            self.redStatus = 'on'
            _, _ = subprocess.getstatusoutput(red_off)
            _, _ = subprocess.getstatusoutput(red_on)
            self.redLightButton.setText('Red On')
            self.redBlinkButton.setText('Red Off')

    def red_blink_clicked(self):
        self.redBlinkButton.clearFocus()
        if self.redStatus == 'off':
            self.redStatus = 'blink'
            _, _ = subprocess.getstatusoutput(red_blink)
            self.redBlinkButton.setText('Red Off')
        elif self.redStatus == 'on':
            self.redStatus = 'blink'
            _, _ = subprocess.getstatusoutput(red_off)
            _, _ = subprocess.getstatusoutput(red_blink)
            self.redBlinkButton.setText('Red Off')
        elif self.redStatus == 'blink':
            self.redStatus = 'off'
            _, _ = subprocess.getstatusoutput(red_off)
            self.redLightButton.setText('Red On')
            self.redBlinkButton.setText('Red Blink')

    def yellow_clicked(self):
        self.yellowLightButton.clearFocus()
        if self.yellowStatus == 'off':
            self.yellowStatus = 'on'
            _, _ = subprocess.getstatusoutput(yellow_on)
            self.yellowLightButton.setText('Yellow Off')
        elif self.yellowStatus == 'on':
            self.yellowStatus = 'off'
            _, _ = subprocess.getstatusoutput(yellow_off)
            self.yellowLightButton.setText('Yellow On')
        elif self.yellowStatus == 'blink':
            self.yellowStatus = 'on'
            _, _ = subprocess.getstatusoutput(yellow_off)
            _, _ = subprocess.getstatusoutput(yellow_on)
            self.yellowLightButton.setText('Yellow Off')
            self.yellowBlinkButton.setText('Yellow Blink')

    def yellow_blink_clicked(self):
        self.yellowBlinkButton.clearFocus()
        if self.yellowStatus == 'off':
            self.yellowStatus = 'blink'
            _, _ = subprocess.getstatusoutput(yellow_blink)
            self.yellowBlinkButton.setText('Yellow Off')
        elif self.yellowStatus == 'on':
            self.yellowStatus = 'blink'
            _, _ = subprocess.getstatusoutput(yellow_off)
            _, _ = subprocess.getstatusoutput(yellow_blink)
            self.yellowBlinkButton.setText('Yellow Off')
        elif self.yellowStatus == 'blink':
            self.yellowStatus = 'off'
            _, _ = subprocess.getstatusoutput(yellow_off)
            self.yellowLightButton.setText('Yellow On')
            self.yellowBlinkButton.setText('Yellow Blink')

    def green_clicked(self):
        self.greenLightButton.clearFocus()
        if self.greenStatus == 'off':
            self.greenStatus = 'on'
            _, _ = subprocess.getstatusoutput(green_on)
            self.greenLightButton.setText('Green Off')
        elif self.greenStatus == 'on':
            self.greenStatus = 'off'
            _, _ = subprocess.getstatusoutput(green_off)
            self.greenLightButton.setText('Green On')
        elif self.greenStatus == 'blink':
            self.greenStatus = 'on'
            _, _ = subprocess.getstatusoutput(green_off)
            _, _ = subprocess.getstatusoutput(green_on)
            self.greenLightButton.setText('Green Off')
            self.greenBlinkButton.setText('Green Blink')

    def green_blink_clicked(self):
        self.greenBlinkButton.clearFocus()
        if self.greenStatus == 'off':
            self.greenStatus = 'blink'
            _, _ = subprocess.getstatusoutput(green_blink)
            self.greenBlinkButton.setText('Green Off')
        elif self.greenStatus == 'on':
            self.greenStatus = 'blink'
            _, _ = subprocess.getstatusoutput(green_off)
            _, _ = subprocess.getstatusoutput(green_blink)
            self.greenBlinkButton.setText('Green Off')
        elif self.greenStatus == 'blink':
            self.greenStatus = 'off'
            _, _ = subprocess.getstatusoutput(green_off)
            self.greenLightButton.setText('Green On')
            self.greenBlinkButton.setText('Green Blink')


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
        self.camera = PiCamera()
        self.rawCapture = PiRGBArray(self.camera)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="rgb", use_video_port=True)
        # self.stream = cv2.VideoCapture(src)
        self.frame = None
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        for f in self.stream:
            # grab the frame from the stream and clear the stream in
            # preparation for the next frame
            self.frame = f.array
            self.rawCapture.truncate(0)

            # if the thread indicator variable is set, stop the thread
            # and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


app = QtWidgets.QApplication(sys.argv)
app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
screen_resolution = app.desktop().screenGeometry()
width, height = screen_resolution.width(), screen_resolution.height()
window = SimpleVideoGui(None)
window.setWindowTitle('Simple Video GUI')
window.show()
app.exec_()
