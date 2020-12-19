# Team11: 

## File overview and existing bug notes

Source code present is as follows:
* settings.py: For gameplay settings such as number of players, whether the current device is a Pi, and so on. A few settings which were not critical for building the prototype are currently hardcoded inside the game and pending update. For gameplay this is intended as an intermediate solution, to be replaced by a GUI settings menu and detection of other relevant information.
* main.py: Run to play. See play instructions below. This file contains the high level logic based around threading and communications. Launching an interactive settings menu is not yet implemented.
* comms.py: Contains all of the communications classes. There are currently some observed issues with dropped and repeated messages, which will be resolved for the final version.
* gameplay.py: Contains classes for the game and the playspace, as managed by the central node. Individual players also launch instances of the playspace, but don't perform any logic. The checkCollision logic is currently under review to correct behavior when vertical and horizontal axes are not at their default settings. The display implementation in OpenCV is intended as a prototype, to be replaced with a Unity implementation.
* playerPC.py: Contains classes for the player PC and the webcam and microphone integrations.
* playerPi.py: Contains classes for the player Pi and the IMU integrations.
* unittests.py: Contains unit tests, currently only testing a subset of logic in gameplay.py. Additional tests to be added.
* IMU.py, LIS3MDL.py. LSM6DSL.py, LSM9DS0.py, LSM9DS1.py: these files are all directly from the Berry IMU sample code, with a minor modification to the smbus import in IMU.py to support Python 3.7+.

## Sources

Gesture recognition (in the BerryIMU class in playerPi.py) is an adaptation of the BerryIMU code. Originally retrieved 10/22/2020:
https://github.com/ozzmaker/BerryIMU/tree/master/python-BerryIMU-gryo-accel-compass-filters 

Voice recognition (in the Microphone class in playerPC.py) is an adaptation of the speech recognition library example code. Originally retrieved 10/30/2020: 
https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__main__.py 

Pose recognition (in the Camera class in playerPC.py) is mostly custom, but uses code for finding extreme points from the OpenCV contour documentation. Originally retrieved 11/30/2020:
https://docs.opencv.org/master/d1/d32/tutorial_py_contour_properties.html

Pose recognition code for selecting contours with specific hierarchies was borrowed from an implementation found on Stack Exchange. Originally retrieved 12/7/2020:
https://stackoverflow.com/questions/52397592/only-find-contour-without-child 

## Current game state

This version of the game is a prototype, with gesture, pose, and voice detection incorporated. An end game condition is not yet implemented, which is to say it's currently on infinite play mode.

### Gesture Detection
The gesture detection algorithm simply checks the angle of the IMU based on accelerometer data. A median filter is used to exclude outlier reads. The angles were set based on experimentation. Due to the simplicity of the design, the device reads consistently when properly used, and failure to read the desired direction indicates a need to adjust the choice of angles. it is expected to give bad reads when improperly used. For example, if put down on its left side, it will consistently read “left” until moved to a different orientation. Future development of this algorithm will include refining those angles based on more than one user's range of motion; a potential future replacement to this algorithm would be based on actual motion of the IMU, rather than simply its orientation.

### Pose Recognition
Earlier efforts to develop pose detection using convex hull matching were discarded, along with many other OpenCV options, as it turned out that the current version of OpenCV disables many of the better matching algorithms due to proprietary concerns. Instead we went with a simpler algorithm that obtains contours, selects a subset of those contours based on hierarchy and area to identify a shape likely to be an arrow, and performs some simple arithmetic evaluations on extreme points to ensure that the shape is likely to be an arrow of a particular orientation. This has a decent accuracy rate, although still has some false positives whose resolution we are exploring. We are still pursuing a machine learning option for arrow recognition, and will use the option which performs better.

A critical discovery in the pose detection implementation was that it was challenging for the player to know where to hold the arrow to ensure that it could be read. We addressed this issue by adding a webcam feed with a target square to the display. This worked well, and required some adjustments to the display design as well as to the backend design due to Mac restrictions for OpenCV display and camera behavior.

### Voice Recognition
Voice recognition performs with some lag and failure to read, so we are limiting its overall use to cases where near-instant response is not critical. We are also exploring ways to improve the read quality, such as extending the length of desired keywords. In the current version of the game, we are only processing the “ready” command. In order for the game to start, every player must say that command to indicate that they are indeed: ready.

### Communications
Communications are implemented using MQTT. The system is largely working well, although some intermittent issues exist with unexpectedly lost or repeated messages. Erroneously repeated messages will be filtered out using a message ID tracking system which will ignore messages which have already been received from a particular client. This will be lightweight, as redundant messages all seem to be repeats of the most recent message a client has sent, so only the most recent message ID for each client (up to the number of game players) will need to be stored. Missed messages are a trickier problem. We have only observed missed messages so far in which the pi transmits information about a rotation and the central node does not receive it, but it is possible other messages are getting missed as well. Some missed messages are low risk -- for example, if information about a rotation is missed, it isn’t ideal but the player can simply try rotating again. However, if the volume of missed messages is high that is a greater concern. This is under review, along with a review of if changing the quality of service will help.

### Play Area Logic
The logic for managing player activity within the play area proved to be significantly complicated. After all player dynamics were thought to be accounted for in the initial playspace, when a player would do a rotation, a lot of the dynamic code (collisions, tags, etc.) failed. To help ensure predictable behavior and minimize discovery of bugs in playtesting, a unit testing suite was developed. This was very effective in helping to ensure accurate behavior for the plane of action which these unit tests used. Player interaction is generally dictated by the euclidean distance between players and anything in their field of motion. This proved successful for players moving at unit speed but issues began to arise with players moving at a faster speed such as the tagged player. This issue was mitigated by comparing the deterministic position of this player before and after projected movement, and comparing it to other members of the playspace. The solution helped avoid issues of players in the corner or sides not getting tagged, as well as unidentified collision when the player is approaching from a distance. Unit tests are being built accordingly to support the scope of the 3 dimensional logic and to guarantee consistent and accurate player movement. A few minor issues also remain that we hope to solve next quarter such as players potentially spawning on the same location, or overlapping when a rotation of the playspace happens. These issues are lightweight and only require checking other player positions upon spawn or rotation to insure no collisions.

### Threading and Multiprocessing
Use of threading and multiprocessing was determined early on as necessary for gameplay. It also introduced some unexpected complications due to requirements for using OpenCV’s camera access and display behaviors on a Mac. These requirements forced us to place some OpenCV activity in primary threads and multiprocesses, and reorganize other code around it. This does not cause any conflicts with other parts of our game at this time, but we will have to be mindful as we introduce new features into the game which may have similar restrictions on use.

### Display
OpenCV allows generating simple geometric graphics, but does not natively support sprite motion. Therefore, moving or removing something from the play area requires either overwriting that area of the display with the background, or redrawing the entire space. We opted for redrawing the entire space upon any player motion update based on the simple graphics, and this worked fine for the display of the play area on its own. When we began displaying the user’s webcam feed alongside the display, though, the lag was so bad that the webcam feed could not properly be called video. We resolved this by generating a base grid at game startup and saving it, and when updating the play area state, simply making a copy of the base grid and writing current player positions onto it. This sped up the display dramatically such that the video feed now clearly looks like video, although it has some flickering which may be due to these lag issues. This flickering is being treated as low priority due to our plans to replace the OpenCV display with one implemented in Unity. In the event that Unity does not perform as desired and we determine that OpenCV is the best choice for the display, we will prioritize resolution of the flickering issue.

## Future Plans

Aside from resolving bugs identified above, here are our goals for next quarter:
* Improve hardware integration accuracy and responsiveness
* Implement the display in Unity
* Add an interactive settings menu
* Add obstacles and powerups, with multiple variants: regular walls to block motion and ice walls to freeze players, powerups that boost speed or swap a player's position with someone else, and more
* Soundtrack
* Sound effects
* Different gameplay modes: computer plays it/last man standing, round based/strategy, and more