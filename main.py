# Main file for the Exercise program

# Prerequisites:
# PySimpleGUI

# Parameters:
# Path to recorded exercise images
# Path to practice exercise images, to be recorded every session

# import webcam.py for saving videos
import webcam
# contains subprograms and menus, as well as recording poses
import graphics

import PySimpleGUI as sg
import cv2

# for storing various data objects
import pickle
# for session goals
import datetime

# some settings for customisation
program_title = "Exercise Helper"
theme = "DarkGreen"
icon = "icons/trophy.png"

# the total number of reps in the session
sessionReps = 0
todayReps = 0
# the goal number of reps per day
dailyGoal = 30

# Step 1 - Main Menu

# change the look and feel of the program
sg.theme(theme)
# menu options
layout = [
    # add some information about the program
    [sg.Text('Welcome!', size=(10, 1), font=('Helvetica 20'))],
    # add various options for the user to do
    [sg.Button('Practice exercise', size=(10, 1), font=('Helvetica 20'))],
    [sg.Button('Record exercise', size=(10, 1), font=('Helvetica 20'))],
    [sg.Text('Rep Goal:', size=(10, 1), font=('Helvetica 20')),
     sg.Text('', size=(10, 1), font=('Helvetica 20'), key='-repGoal-')],
    [sg.Button('Exit', size=(10, 1), font=('Helvetica 20'))]
]


#try and load exercise database
exerciseDB = {}
try:
    exerciseDBFile = open("exerciseDB.p", "rb")
    exerciseDB = pickle.load(exerciseDBFile)
    exerciseDBFile.close()
except FileNotFoundError:
    pass

# load session data on the number of reps
# dictionary with the date and the number of reps on that date
sessionData = {}
try:
    sessionDBFile = open("sessionData.p", "rb")
    sessionData = pickle.load(sessionDBFile)
    sessionDBFile.close()
except FileNotFoundError:
    pass

window = sg.Window(program_title, layout, no_titlebar=False, location=(0,0))
window.Finalize()

# today's date
todayDate = str(datetime.datetime.today().date())
if todayDate in sessionData.keys():
    todayReps = sessionData[todayDate]

while True:
    # event loop
    event, values = window.read()
    window['-repGoal-'].update(str(todayReps) + "/" + str(dailyGoal))
    if event in (None, 'Exit'):
        break
    if event == "Practice exercise":
        exerciseChoice = graphics.selectExerciseToPractice(exerciseDB)
        if exerciseChoice != "":
            sessionReps = graphics.practiceExercisePose(exerciseDB[exerciseChoice])
            todayReps += sessionReps
            sessionData[todayDate] = todayReps
    if event == "Record exercise":
        # record various positions
        # e.g. up and down stages of a pushup
        exerciseName = graphics.recordExerciseName()
        if exerciseName in exerciseDB.keys():
            popup("That exercise name is already in the database!")
        else:
            # record the poses
            poses = {}
            recordAnother = True
            while recordAnother:
                new_pose_name, recordAnother = graphics.recordPoseName()
                exercisePose = graphics.recordExercisePose()
                if exercisePose == []:
                    sg.popup("You haven't recorded anything!")
                else:
                    poses[new_pose_name] = exercisePose
            exerciseDB[exerciseName] = poses
    window.Refresh()

# save exercises to database
sg.popup("Saving exercises to database, click OK to continue")

exerciseDBFile = open("exerciseDB.p", "wb")
pickle.dump(exerciseDB, exerciseDBFile)
sessionDBFile = open("sessionDB.p", "wb")
pickle.dump(sessionData, sessionDBFile)

# stop recording
webcam.endVideo()

# close window
window.close()
