# Honey

The application was written as a final scripting languages project. Python was used as the programming language. <br /> The GUI was created using Kivy and KivyMD but no kv files were used due to final project requirements.<br /><br />
This version of the application has been developed and tested only on the PC platform. However, Kivy allows the application to be used on mobile devices. Therefore, some code is already made to be used on Android and iOS, but no testing has been undertaken.<br/>
App uses trained ML model developed by Mediapipe Google to perform calculations and create mesh on face with 468 landmarks.
Thanks to that we are able to use them and add layers, images and other stuff like analysing posture, expression etc. <br/> <br/>

Link to Mediapipe website: https://google.github.io/mediapipe/ <br/>
Link to Kivy website: https://kivy.org/ <br/><br/>

An application has two main purposes:
  * Apply Snapchat-like filters on the live camera image like: dog filter with nose, ears and tongue, space helmet with space background, devil horns, funny eyes and green face mesh. <br>
The dog filter has a special ability to detect if the mouth is open so it can overlay the tongue on them only when the person opens their mouth.

  * Edit photo using most popular filters like: greyscale, sepia, pencil sketch, invert, summer effect, winter effect, gotham effect, canny, cartoon, brightness and darkness control.
  
## Table of contents:
* [Technologies](#technologies)
* [Illustrations](#illustrations)
 
## Technologies
Project is created with:
* Python
* Kivy
* KivyMD
* OpenCV
* Mediapipe
* Numpy

## Illustrations
In the following illustrations only static photos were used to show abilities of app. However, the application uses a normal live camera and applies the filters on user.
<p float="left">
  
</p>
