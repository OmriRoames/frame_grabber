#!/bin/python

__author__ = 'Giuseppe Battista'
__url__ = 'http://giusedroid.blogspot.com'

HELP_MESSAGE = """Script: frame_grabber.py
Usage: python frame_grabber.py path/to/video
Requires: OpenCV 2.4.8+
Purpose: Select and save frames from a given video.
Commands:
    Key             Function
    a               previous frame
    d               next frame
    q               exit
    SHIFT + a       skip 10 frames forward
    SHIFT + d       skip 10 frames backwards
    s               saves current frame
    dbl click       saves current frame

Controls:
    Slider          Navigate through the video

More info: http://giusedroid.blogspot.com
"""

# Check if the user has provided a path to a file
# otherwise display the HELP_MESSAGE

import os
import sys
import time as t


# Check if OpenCV module is present
# otherwise stop the application

try:
    import cv2
except ImportError as e:
    print("Fatal Error: Could not import OpenCV, ", e)
    exit(-1)
else:
    print ("Using OpenCV ", cv2.__version__)

# these flags may depend on your opencv version:
# in opencv 3.0.0 these flags are implemented as
# cv2.CAP_PROP_POS_FRAMES and
# cv2.CAP_PROP_FRAME_COUNT
#CURRENT_FRAME_FLAG = cv2.cv.CV_CAP_PROP_POS_FRAMES
#TOTAL_FRAMES_FLAG = cv2.cv.CV_CAP_PROP_FRAME_COUNT

CURRENT_FRAME_FLAG = cv2.CAP_PROP_POS_FRAMES
TOTAL_FRAMES_FLAG = cv2.CAP_PROP_FRAME_COUNT


WIN_NAME = "Frame Grabber"
POS_TRACKBAR = "pos_trackbar"

VIDEO_PATH = None


import easygui # easy_install easygui


try:
    VIDEO_PATH = sys.argv[1]
except IndexError as e:
    print(HELP_MESSAGE)
    exit(-1)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("Fatal Error: Could not open the specified file.")
    exit(-1)

ret, frame = cap.read()
length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print("%s has %s frames" % (VIDEO_PATH, length))


if not ret:
    print("Fatal Error: Could not read/decode frames from specified file.")
    exit(-1)


def dummy():
    pass


def save_image():
    filename = "image_%0.5f.png" % t.time()
    cv2.imwrite(filename, frame)


def seek_callback(x):
    global frame
    i = cv2.getTrackbarPos(POS_TRACKBAR, WIN_NAME)
    cap.set(CURRENT_FRAME_FLAG, i-1)
    _, frame = cap.read()
    cv2.imshow(WIN_NAME, frame)


def mouse_callback(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        save_image()


def skip_frame_generator(df):

    def skip_frame():
        global frame
        cf = cap.get(CURRENT_FRAME_FLAG) - 1
        cap.set(CURRENT_FRAME_FLAG, cf+df)
        cv2.setTrackbarPos(POS_TRACKBAR, WIN_NAME, int(cap.get(CURRENT_FRAME_FLAG)))
        _, frame = cap.read()
    return skip_frame


def select_roi():
    x, y, w, h = cv2.selectROI(WIN_NAME, frame)
    cx = x
    cy = int(y + 0.1*h)
    img = cv2.rectangle(frame, (x, y), (x + w, y + h), color=(0, 0, 255), thickness=3)
    cv2.imshow(WIN_NAME, img)
    message = easygui.enterbox(msg="Enter some text below!",
                               title="Title of window",
                               strip=False,  # will remove whitespace around whatever the user types in
                               )
    cv2.putText(img, message, (cx, cy), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), thickness=4)
    cv2.imshow(WIN_NAME, img)
    current_frame_index = cap.get(CURRENT_FRAME_FLAG)
    filename = os.path.splitext(os.path.basename(VIDEO_PATH))[0] + "_frame_%s_ROI.png" % int(current_frame_index)
    cv2.imwrite(filename, img)


cv2.namedWindow(WIN_NAME, flags=cv2.WINDOW_NORMAL)
cv2.createTrackbar(POS_TRACKBAR, WIN_NAME, 0, int(cap.get(TOTAL_FRAMES_FLAG)), seek_callback)
cv2.setMouseCallback(WIN_NAME, mouse_callback)

actions = dict()

actions[ord("D")] = skip_frame_generator(10)
actions[ord("d")] = skip_frame_generator(1)
actions[ord("a")] = skip_frame_generator(-1)
actions[ord("A")] = skip_frame_generator(-10)
actions[ord("q")] = lambda: exit(0)
actions[ord("s")] = save_image
actions[ord("r")] = select_roi


cv2.resizeWindow(WIN_NAME, 2400, 1600)

play_video = True

while True:
    if play_video:
        ret, frame = cap.read()
        cv2.imshow(WIN_NAME, frame)
        print(int(cap.get(CURRENT_FRAME_FLAG)))

    key = cv2.waitKey(120) & 0xFF
    if key == ord('p'):
        play_video = not play_video
    actions.get(key, dummy)()







