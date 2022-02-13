# Codesec Submission Program
# Team - The Codons

This program is an experimental version of an exercise helper app for the desktop.
The program uses the webcam to make a database of exercises, and then uses pose detection in order to improve the user's form while exercising and count the number of repetitions of that exercise, along with a daily goal feature.

Prerequisites:
This program has been tested to work on Arch Linux.
Required libraries:
* PySimpleGUI
* OpenCV (headless version)
* imageio
* PIL
* io
* TensorFlow
* TensorFlow Hub
* TensorFlow Docs
* NumPy
* MatPlotLib
* IPython
* the MoveNet algorithm (see https://www.tensorflow.org/hub/tutorials/movenet for more details)

How to operate:
Download the project and run main.py in Python 3

# Copyright

model.tflite is work created and shared by Google under the Apache License.

Portions of the movenet.py file are modifications based on work created and shared by Google and used according to terms described in the Apache 2.0 License:

Copyright (c) 2022, Google
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
