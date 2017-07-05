# Video GUIs

This repository contains the following GUIs for displaying an OpenCV video feed in a PyQT5 GUI:

- PyQt5Test.py:       Quick and simple file to double check that everything is working correctly.
- ThreadingVideoGUI:  Updates the video stream from a QThread that reads the frames from a polled webcam thread.
- QLight-VideoGUI:    Adds onto ThreadingVideoGUI by giving the user control over a QLight (USB stacklight)
- SimpleVideoGUI:     Updates video stream from a polled webcam. 


Each folder contains a requirements.txt to make sure the required packages are installed.
