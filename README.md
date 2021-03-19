# Team11: 

## File overview and existing bug notes

Source code present is as follows:
* settings.py: For setting a unique MQTT string prefix. All players should use the same unique string when playing the game, and should use a different string from anyone else playing the game in a different group.
* main.py: Run to play. See play instructions below. This file contains the high level logic based around threading and communications. Launching an interactive settings menu is not yet implemented.
* comms.py: Contains all of the communications classes. There are currently some observed issues with dropped and repeated messages, which will be resolved for the final version.
* gameplay.py: Contains classes for the game and the playspace, as managed by the central node. Individual players also launch instances of the playspace, but don't perform any logic. The checkCollision logic is currently under review to correct behavior when vertical and horizontal axes are not at their default settings. The display implementation in OpenCV is intended as a prototype, to be replaced with a Unity implementation.
* playerPC.py: Contains classes for the player PC and the webcam and microphone integrations.
* playerPi.py: Contains classes for the player Pi and the IMU integrations.
* unittests.py: Contains unit tests, currently only testing a small subset of logic in gameplay.py. Additional tests to be added.
* IMU.py, LIS3MDL.py. LSM6DSL.py, LSM9DS0.py, LSM9DS1.py: these files are all directly from the Berry IMU sample code, with a minor modification to the smbus import in IMU.py to support Python 3.7+.

Additional files present:
* Virtual-Tag-Instructions.pdf: installation instructions and control arrow

Not included:
* Soundtrack and sound effect wav files. Game can run without these items, it just doesn't sound as cool. These may get loaded to a repository for general access at a later time.

## Sources

Gesture recognition (in the BerryIMU class in playerPi.py) is an adaptation of the BerryIMU code. Originally retrieved 10/22/2020:
https://github.com/ozzmaker/BerryIMU/tree/master/python-BerryIMU-gryo-accel-compass-filters 

Voice recognition (in the Microphone class in playerPC.py) is an adaptation of the speech recognition library example code. Originally retrieved 10/30/2020: 
https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__main__.py 

Pose recognition (in the Camera class in playerPC.py) is mostly custom, but uses code for finding extreme points from the OpenCV contour documentation. Originally retrieved 11/30/2020:
https://docs.opencv.org/master/d1/d32/tutorial_py_contour_properties.html

Pose recognition code for selecting contours with specific hierarchies was borrowed from an implementation found on Stack Exchange. Originally retrieved 12/7/2020:
https://stackoverflow.com/questions/52397592/only-find-contour-without-child 

## Basic Design

Virtual Tag is a multiplayer game developed in Python which players control using gesture, pose, and voice detection. Gestures are obtained with an IMU mounted on a Raspberry Pi. Pose and voice are detected using a webcam and microphone respectively, connected to the player’s computer. All gameplay is remote.

Each player connects their devices and says “ready”, and then the game starts. The game places the players in a 3D space, viewed as a 2D projection onto a particular plane. One player is “it” and has the goal of tagging another player, making that other player the new “it”. Players chase each other around the 2D projection by pointing a printed arrow left, right, up, or down for their webcam to see. If a player wants to make a hasty escape, get closer to a far player, or just stir up some chaos, they have options. One option is to use their IMU to rotate the projected playspace left, right, forward, or backward. This causes the projection to change: as the players are all in 3D space, each player also has a position in the previously hidden dimension which can now be used to show their new location. All player interaction only occurs in the current projection. The player’s other option is to use powerups, scattered around the play area, which can be used briefly to provide a speed boost or to freeze all other players. Obstacles may be scattered around the play area as well, interfering with player motion and allowing for new angles of strategic play. Many variants for obstacles and powerups as well as general gameplay are possible through user selection.

Gesture detection is performed using a BerryIMU connected to a Raspberry Pi via I2C. The IMU is rotated in one of four directions (forward, backward, right, and left) to rotate the playspace upon its axes. The BerryIMU provided code was adapted for this purpose. The angles of orientation are read, and then smoothed with a median filter to avoid outlier data. The smoothed angles are then classified based angle thresholds. Once a rotation is performed, a cooldown hold is applied to prevent constant rotations. As the game is played sitting, the Pi can be used while plugged into a computer or to the wall rather than on a battery.

Pose recognition is performed using OpenCV. The player’s webcam captures images of the player, who holds a printed controller arrow which OpenCV can then classify to move the player (up, down, left, and right) around the playspace. The controller arrow, included in the instructions, has specific characteristics to make it easy to identify: solid black fill on white background, polygon area, ratio of length to width, and ratio of head to tail. OpenCV is used to obtain image contours. Contours which contain no other contours, and which have an appropriate area of the image relative to the rest of the image, are determined likely to be an arrow, and are evaluated for the positions of their extreme top, bottom, left, and right points. On a vertical arrow, for example, the top point is the extreme front point of the arrow head, the bottom point is the far end of the tail, and the left and right points are the extreme side points on the wings of the arrow head. This arrow is classified by:
* The ratio of top to bottom vertical distance to the left to right horizontal distance, indicating the arrow is more vertical than horizontal
* The top and bottom points falling within a certain horizontal distance relative to the shape width, indicating a sufficiently vertical arrow for classification (for a more horizontal arrow, the left and right points are used)
* The ratio of top to left/right point horizontal distance to left/right to bottom horizontal distance, indicating the shorter head is at the top above the longer tail
Arrow poses cause player motion around the game, and so set the primary action for gameplay. A brief delay of half a second is applied before a new arrow pose can be read and classified, to provide a good pace which is rapid but not beyond control.

Voice recognition is used to announce the player is ready for the game, to use a powerup, or to drop a powerup (“ready”, “powerup”, and “drop” respectively). It uses Python’s Speech Recognition library and Google’s speech recognition API. Example code from the Speech Recognition library was adapted for this purpose. This library and API can have trouble identifying when to stop listening to input and begin classifying it, so we set a cutoff time of three seconds due to the short length of our key phrases.

Remote communication is implemented using Eclipse Paho MQTT with the EMQ X free public broker. This makes gameplay multiplayer, with players able to participate from anywhere with an internet connection. Game logic is hosted on the computer of one “primary” player and then game status is transmitted out to all player devices, so the primary player should have a faster internet connection.

The display is implemented using OpenCV’s graphical capabilities. The constraints of this tool result in frame by frame updates of a static image, with some limits to effective display of text based data on screen. Due to these limits, an upper limit of 9 players and 20x20 playspace size are set, and all player motion is discrete motion from grid position to grid position on the playspace rather than fluid motion between these positions.

The soundtrack and sound effects were implemented using Pygame. The soundtrack was created in MuseScore 3, a software that allows for music composition and the ability to download music composed as .wav files. The soundtrack in the settings menu was a custom composition. The soundtrack during gameplay was adapted from a YouTube video Trance Music for Racing Game from the channel Bobby Cole. Sound effects play for in game events, such as upon use of a powerup. These were obtained from Zapsplat’s royalty free sound effects library.

## Current game state

We have developed a nearly complete product, which is fully playable according to our original design. To make the game ready for distribution:
* It should be delivered as an executable so that players do not need to deal with setting up an environment or installing libraries.
* On launch, an option is needed to enter a unique game code to set the MQTT topic and thus join a particular game.
* Permission needs to be obtained for use of our Bobby Cole adaptation for the soundtrack due to key similarities, or an alternate soundtrack developed to avoid copyright issues.
Additional changes could be rolled in to a final build for distribution, covered below.
Overall, most of our key goals were met. Some things were achieved ahead of time, while others took more time than expected. We accomplished the following:
* Completely playable game, with prototype developed by end of fall quarter
* Nice looking, responsive display and functional settings menu
* Multiple gameplay modes (infinite and last person tagged wins)
* Powerups with multiple modes (freeze and speed)
* Obstacles
* Ability to dynamically choose the number of players, powerups, and obstacles; play area size; and gameplay mode
* One custom soundtrack piece and one adapted soundtrack piece
* Sound effects on key game events
* Exception handling to ensure that unexpected behavior during gameplay generally does not cause the game to end, and logging to support troubleshooting when issues occur
* Threading and multiprocessing to manage game events and logic
* Well-structured code which is ready for future enhancements such as addition of new gameplay modes and powerups
* Multiplayer functionality with up to 9 players at a time
Not everything went as expected. Some key changes and choices were made due to discoveries and delays in the development process.
* For pose recognition, there were multiple OpenCV based approaches that we pursued however they failed to be implemented due to difficulties in building the code and the amount of lag certain processes caused the display. This included a pose detection algorithm that used bounding boxes around contours, a pose detection algorithm that used Canny Edge Detection to detect the edges of the arrow, and a pose detection algorithm that used template matching to detect the arrow and the position the arrow is in. We also pursued a machine learning approach as well. This took too much time for too little payoff, so we focused instead on refining the contour based algorithm.
* Gesture recognition as implemented is simply orientation recognition. Our team faced delays in receiving hardware, limiting the ability to pass off development of this task to someone with more time. As the orientation recognition performed with high reliability, as long as the base orientation of the device was respected, it was considered sufficient.
* The game logic turned out to take more time than expected. Development of scripted unit tests was intended to help manage this issue, but that tool wound up not being used and so bugs wound up frequently found in playtesting. To ensure a complete game could be developed, we focused on optimizing the base functionality with two powerups and two gameplay modes, rather than completing the full suite of powerups and gameplay modes originally imagined. Additionally, we determined that some bugs were lower priority and acceptable for the delivered product. These were bugs which caused minor display errors resolved by continuing to play the game (for example, powerups leaving a shadow after being picked up) as well as bugs causing undesired but low impact, rare behavior (for example, a player tagging another player through an obstacle).
* The OpenCV display and settings menu were intended as prototypes, with the goal to use Unity instead. However, it turned out that Unity is not easily compatible with our version of Python, a version which was required by other game libraries. We then explored using PyGame, already in use for the sound effects, but development efforts in PyGame for the display and settings menu were not completed in time. The display logic for OpenCV was vastly different than what would be needed for PyGame, since PyGame functions by updating a sprite whereas OpenCV refreshes the frame. A PyGame settings menu was created. However, the new menu version involved the user setting the custom parameters sequentially across multiple pages. Though the PyGame menu had aesthetic potential, the sequential input of each parameter proved to be a bad UX for the player. Instead, after discussion, we decided to stick with the OpenCV menu since all the parameters were visible and modifiable on the same page. In hindsight, an alternate goal of ours could have been to pursue either PyGame or Unity from the start of development.
* Distribution as an executable remains needed, but as this was not necessary for product demonstration it was deprioritized.
* We experienced challenges in operating system compatibility with the OpenCV, Speech Recognition, and PyGame libraries, which had different behavior on Mac and Windows platforms. Issues on the Mac were resolved. Issues on the PC could not be. We consider the game optimized for Mac performance.
* Exception handling and logging were implemented, but due to time and code sharing limitations we chose key focus areas rather than completing exception handling and logging for the entire code base.

## Future Plans

Due to limitations on time, some of our goals were shelved in favor of developing a complete and coherent game, but the vision for the game is not done yet. To improve the user experience we want to introduce new power ups, obstacles, and game modes to make the game weirder and more challenging. We would also like to make the game look prettier by implementing settings and display in Pygame or Unity to get a continuous animated player motion. A Unity implementation would require rewriting the game in C#, a massive effort, but one which would also resolve platform compatibility issues. We would also like to add more customization to the interface so users can play the game the way they want, and allow for them to add their vision to the gameplay. This would include settings to adjust the background music. To make it more accessible we would like to implement left-handed gameplay mode, where the game moves the pose recognition capture area and display box to the left side of the camera feed and the camera feed to the left side of the display. To add a more random aspect to the game, we would like to change the default to randomize playspace size, obstacle count, and power up count, unless manually set. Speech recognition in general performs inconsistently enough that it is somewhat disruptive to gameplay, and use of a better API is critical. Finally we would also like to improve robustness and troubleshooting capacity, including more exception handling/logging while delivering the game as an executable.

Based on user feedback, we would also want to change the power up color/shape when a power up is held to inform the player they can’t pick another one up and add a timer display for powerups in the future. We would also like to add a unique soundtrack for when power ups are active and make the base soundtrack loop perfectly. These are all things that could be done in a major update or sequel to Virtual Tag.

Finally, although there are no game-stopping bugs, there are a few that we would resolve in future versions. This includes various issues with powerups, such as a shadow sometimes left after pickup, occasional failure to display the powerup, and occasional issues where powerup messages do not display as expected. Additionally, some issues around player motion behave unexpectedly: when a player has a speed powerup they are supposed to move a greater distance for each movement, or up to that distance if the game edge or an obstacle interferes, but sometimes they are unable to move partial distances to reach an edge or obstacle. Players can even hop over obstacles or tag through them. These issues can all likely be resolved by reworking the logic for moving players and checking collisions, which evolved significantly during game design.
