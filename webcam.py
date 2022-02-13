# Record the user's motion using the webcam
# This requires the opencv library (which will also need to be installed for movenet)
# You also need to configure your computer to use TKinter
# E.g. on Arch Linux, run the command: sudo pacman -S tk
import cv2
import imageio

# GUI libraries
import PySimpleGUI as sg
from PIL import Image
import io

cap = cv2.VideoCapture(0)
# resolution of the camera
size = (cap.get(cv2.CAP_PROP_FRAME_WIDTH),
        cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

def recordVideo():
    # returns a sequence of images recorded from the webcam
    # store the current frames
    frames = []
    image_count = 0
    # setup the GUI for recording
    # define the window layout
    layout = [[sg.Image(filename='', key='-image-')],
        [sg.Button('Start', size=(7,1), pad=((600,0),3), font='Helvetica 10')],
        [sg.Button('Finish', size=(7,1), pad=((600,0),3), font='Helvetica 10')]]
    # create the window
    window = sg.Window('Record your exercise, and press the button to stop recording when you are done.', layout, no_titlebar=False, location=(0,0))
    # locate the elements to update
    image_elem=window['-image-']
    # has recording started?
    isRecording = False
    # loop through each frame while the window is opened
    while True:
        event, values = window.read(timeout=0)
        if event in ('Finish', None):
            break
        if event in ('Start', None):
            isRecording = True
        ret, frame = cap.read()
        image_count += 1
        # the input uses a different colouring scheme to OpenCV
        # so we convert the image
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if isRecording:
            frames.append(rgb_frame)
        # convert the image to something that the GUI can understand, and update it
        imgbytes = cv2.imencode('.png', frame)[1].tobytes()
        image_elem.update(data=imgbytes)
    print("Images added: ", len(frames))
    window.close()
    return frames

def saveGIF(fileName, frames):
    print("Saving GIF file")
    total_frames = len(frames)
    cur_frame = 1
    with imageio.get_writer(fileName, mode="I") as writer:
        for idx, frame in enumerate(frames):
            # Display a progress bar
            sg.one_line_progress_meter('Processing video', cur_frame, total_frames,'Please wait while your video is being saved...')
            cur_frame += 1
            writer.append_data(frame)

def recordFrame():
    ret, frame = cap.read()
    #rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #return rgb_frame
    return frame

def endVideo():
    cap.release()
