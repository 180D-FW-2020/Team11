# Team11

Source code present is as follows:
* settings.py: For gameplay settings such as number of players, whether the current device is a Pi, and so on. A few settings which were not critical for building the prototype are currently hardcoded inside the game and pending update. For gameplay this is intended as an intermediate solution, to be replaced by a GUI settings menu and detection of other relevant information.
* main.py: Run to play. See play instructions below. This file contains the high level logic based around threading and communications.
* comms.py: Contains all of the communications classes.
* gameplay.py: Contains classes for the game and the playspace, as managed by the central node. Individual players also launch instances of the playspace, but don't perform any logic.
* playerPC.py: Contains classes for the player PC and the webcam and microphone integrations.
* playerPi.py: Contains classes for the player Pi and the IMU integrations.
* unittests.py: Contains unit tests, currently only testing logic in gameplay.py.
* IMU.py, LIS3MDL.py. LSM6DSL.py, LSM9DS0.py, LSM9DS1.py: these files are all directly from the Berry IMU sample code, with a minor modification to the smbus import in IMU.py to support Python 3.7+.


Gesture recognition (in the BerryIMU class in playerPi.py) is an adaptation of the BerryIMU code. Originally retrieved 10/22/2020:
https://github.com/ozzmaker/BerryIMU/tree/master/python-BerryIMU-gryo-accel-compass-filters 
Voice recognition (in the Microphone class in playerPC.py) is an adaptation of the speech recognition library example code. Originally retrieved 10/30/2020: 
https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__main__.py 
Pose recognition (in the Camera class in playerPC.py) is mostly custom, but uses code for finding extreme points from the OpenCV contour documentation. Originally retrieved 11/30/2020:
https://docs.opencv.org/master/d1/d32/tutorial_py_contour_properties.html
Pose recognition code for selecting contours with specific hierarchies was borrowed from an implementation found on Stack Exchange. Originally retrieved 12/7/2020:
https://stackoverflow.com/questions/52397592/only-find-contour-without-child 
