import PySimpleGUI as sg
import time

# import movenet.py for getting poses from a video
import movenet
import webcam
import cv2

# for checking how good a certain pose is
import performance

def selectExerciseToPractice(exercises):
    # create a menu with a list of exercises to practice
    layout = [[sg.Text('Select an exercise', size=(10, 1), font=('Helvetica 20'))]]
    for name in exercises.keys():
        layout.append([sg.Button(name, size=(10, 1), font=('Helvetica 20'))])
    layout += [[sg.Button("Exit", size=(10, 1), font=('Helvetica 20'))]]
    window = sg.Window("Select an exercise", layout, no_titlebar=False, location=(0,0))
    while True:
        # event loop
        event, values = window.read()
        if event in (None, "Exit"):
            break
        for exercise in exercises.keys():
            if event == exercise:
                window.close()
                return exercise
    window.close()
    return ""

def recordExerciseName():
    # if the user records nothing, return nothing
    # select the name of the exercise to record
    layout = [
        [sg.Text('Enter the name of your exercise', size=(20,1), font=('Helvetica 20'))],
        [sg.Multiline(size=(30,1), key='textbox')],
        [sg.Button("Ok", size=(10, 1), font=('Helvetica 20'))]
    ]
    text = ""
    # create the window
    window = sg.Window("Record an exercise", layout, no_titlebar=False, location=(0,0))
    while True:
        event, values = window.read()
        if event in (None, "Ok"):
            break
    text = values['textbox']
    window.close()
    return text

def recordPoseName():
    # if the user records nothing, return nothing
    # select the name of the exercise to record
    layout = [
        [sg.Text('Enter the name of your pose (e.g. up or down)', size=(20,1), font=('Helvetica 20'))],
        [sg.Multiline(size=(30,1), key='textbox')],
        [sg.Button("Ok", size=(10, 1), font=('Helvetica 20'))]
    ]
    text = ""
    # create the window
    window = sg.Window("Record a pose", layout, no_titlebar=False, location=(0,0))
    while True:
        event, values = window.read()
        if event in (None, "Ok"):
            break
    text = values['textbox']
    window.close()
    # want to record another exercise?
    recordAnother = False
    answer = sg.popup_yes_no("Do you want to record another pose after this?")
    if answer == 'Yes':
        recordAnother = True
    return text, recordAnother

def recordExercisePose(timerLen=10):
    # record the pose of the user using the webcam
    # use a timer in order to give the user enough time to step away
    # if the user records nothing, return None
    # is timer counting down?
    timerCountdown = False
    exercisePose = []
    win_size = webcam.size
    layout = [[sg.Image(filename='', key='-image-'), sg.Graph(win_size, (0, 0), win_size, key='-graph-')],
            [sg.Button("Record", size=(10, 1), font=('Helvetica 20'))],
            [sg.Button("Cancel", size=(10, 1), font=('Helvetica 20'))],
            [sg.Text('Press record and hold still!', size=(20,1), font=('Helvetica 20'), key='-timer-')]
    ]
    # create the window
    window = sg.Window('Preview', layout, no_titlebar=False, location=(0,0))
    window.Finalize()
    # elements to update
    image_elem = window['-image-']
    graph_elem = window['-graph-']
    start_time = 0
    while (True):
        frame = webcam.recordFrame()
        frame_inference = movenet.run_inference(frame)
        #print(frame_inference)
        event, values = window.read(timeout=0)
        # convert the image to something that the GUI can understand, and update it
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()
        image_elem.update(data=imgbytes)
        graph_elem.erase()
        for joint in frame_inference:
            #print('joint', (joint[1]*640, (1-joint[0])*480))
            graph_elem.DrawPoint((joint[1]*640, (1-joint[0])*480), size=10, color='red')
        for bone in movenet.KEYPOINT_EDGE_INDS_TO_COLOR.keys():
            # for the image to be accurate we need to reflect in the line y=x and also reflect the y coordinates
            coord_1_x =   frame_inference[bone[0]][1]
            coord_1_y = 1-frame_inference[bone[0]][0]
            coord_2_x =   frame_inference[bone[1]][1]
            coord_2_y = 1-frame_inference[bone[1]][0]
            #print('bone', (640*coord_1_x, 480*coord_1_y), (640*coord_1_x, 480*coord_2_y))
            graph_elem.DrawLine((640*coord_1_x, 480*coord_1_y), (640*coord_2_x, 480*coord_2_y),
                                width=7, color='green')

        # check if the user has pressed record or cancel
        if event in (None, 'Done'):
            break
        if event == "Record":
            start_time = time.time()
            # change the value of the time
            timerCountdown = True
        if timerCountdown:
            # format the time to a readable format
            timerTime = str(round(10 - (time.time() - start_time), 1))
            window['-timer-'].update(timerTime)
            if (time.time() - start_time > timerLen):
                # timer has finished,
                # now get the pose data
                exercisePose = frame_inference
                break
        graph_elem.update()
        window.Refresh()
    return exercisePose

def practiceExercisePose(exercise):
    # record the pose of the user using the webcam
    # match it to the given exercise in the database
    win_size = webcam.size
    layout = [[sg.Image(filename='', key='-image-'), sg.Graph(win_size, (0, 0), win_size, key='-graph-')],
            [sg.Button("Exit", size=(10, 1), font=('Helvetica 20'))],
            [sg.Text('Predicted pose is:', size=(20,1), font=('Helvetica 20')),
             sg.Text('', size=(20,1), font=('Helvetica 20'), key='-pose-')],
            [sg.Text('Number of reps:', size=(20,1), font=('Helvetica 20')),
             sg.Text('', size=(20,1), font=('Helvetica 20'), key='-reps-')],
            [sg.Text('Error:', size=(20,1), font=('Helvetica 20')),
             sg.Text('', size=(20,1), font=('Helvetica 20'), key='-err-')],
            [sg.Text('Tip:', size=(20,1), font=('Helvetica 20')),
             sg.Text('', size=(20,1), font=('Helvetica 20'), key='-tip-')]
    ]
    # create the window
    window = sg.Window('Preview', layout, no_titlebar=False, location=(0,0))
    window.Finalize()
    # elements to update
    image_elem = window['-image-']
    graph_elem = window['-graph-']
    start_time = 0
    # record the previous pose in order to check for reps
    prevPose = ""
    # count reps
    reps = 0
    while (True):
        frame = webcam.recordFrame()
        frame_inference = movenet.run_inference(frame)
        #print(frame_inference)
        event, values = window.read(timeout=0)
        # convert the image to something that the GUI can understand, and update it
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()
        image_elem.update(data=imgbytes)
        graph_elem.erase()
        for joint in frame_inference:
            #print('joint', (joint[1]*640, (1-joint[0])*480))
            graph_elem.DrawPoint((joint[1]*640, (1-joint[0])*480), size=10, color='red')
        for bone in movenet.KEYPOINT_EDGE_INDS_TO_COLOR.keys():
            # for the image to be accurate we need to reflect in the line y=x and also reflect the y coordinates
            coord_1_x =   frame_inference[bone[0]][1]
            coord_1_y = 1-frame_inference[bone[0]][0]
            coord_2_x =   frame_inference[bone[1]][1]
            coord_2_y = 1-frame_inference[bone[1]][0]
            #print('bone', (640*coord_1_x, 480*coord_1_y), (640*coord_1_x, 480*coord_2_y))
            graph_elem.DrawLine((640*coord_1_x, 480*coord_1_y), (640*coord_2_x, 480*coord_2_y),
                                width=7, color='green')

        # check if the user has pressed record or cancel
        if event in (None, 'Exit'):
            break
        # check the exercise against the database
        best_pose, best_diff, min_err = performance.make_prediction(exercise, frame_inference)
        if prevPose == "":
            prevPose = best_pose
        if best_pose != prevPose and min_error < performance.max_error:
            # we can say with reasonable accuracy that the pose has changed
            # 1 change in pose = 0.5 reps
            reps += 0.5
        window['-pose-'].update(best_pose)
        window['-err-'].update(str(round(min_err, 0.1)))
        window['-tip-'].update(performance.generate_suggestion(best_diff))
        window['-reps-'].update(str(round(reps)))
        graph_elem.update()
        window.Refresh()
    return reps
