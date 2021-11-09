#!/usr/bin/python3

from imutils.video import VideoStream
import argparse
import logging
import signal
from sys import exit
import datetime
import imutils
import os
import time
import cv2
from setting import IMAGES_DIR


def clean_cv():
    logging.info(f"[+] Clearing up camera and opened windows...")
    # cleanup the camera and close any open windows
    vs.release()
    cv2.destroyAllWindows()
    logging.info("[*] Done")


def sig_hdlr(sigin, frame):
    logging.info("[-] Caught signal {}: exiting...".format(sigin))
    clean_cv()
    logging.info("[*] Exiting")
    exit(0)

signal.signal(signal.SIGINT, sig_hdlr)
signal.signal(signal.SIGTERM, sig_hdlr)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--min-area", type=int, default=2000, help="minimum area size")
ap.add_argument("-d", "--debug", help="set logging level to debug", action="store_true")
args = ap.parse_args()
if args.debug:
    logging.basicConfig(level='DEBUG')
args = vars(ap.parse_args())

logging.info("[+] Starting video capture...")
vs = cv2.VideoCapture(0)
time.sleep(2.0)
logging.info("[*] Done")

# initialize the first frame in the video stream
firstFrame = None

frame_rate = 0.5
prev = 0

logging.info(f"[*] Starting main loop (framerate: {frame_rate})")
# Main loop
while True:

    time_elapsed = time.time() - prev
    _, frame = vs.read()

    if not (time_elapsed > 1./frame_rate):
        continue
    
    prev = time.time()


    # grab the current frame and initialize the occupied/unoccupied
    # text
    frame = frame
    text = "Unoccupied"
    # if the frame could not be grabbed, then we have reached the end
    # of the video
    if frame is None:
        logging.critical("[-] Unable to get the first video frame. Ending gracefully.")
        break

    # resize the frame, convert it to grayscale, and blur it
    frame = imutils.resize(frame, width=500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # if the first frame is None, initialize it
    if firstFrame is None:
        logging.debug("[*] Initializing first frame...")
        firstFrame = gray
        logging.debug("[*] Done")
        continue

    logging.debug("[+] Starting computing...")
    # compute the absolute difference between the current frame and
    # first frame
    frameDelta = cv2.absdiff(firstFrame, gray)
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    # dilate the thresholded image to fill in holes, then find contours
    # on thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # loop over the contours
    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        text = "Occupied"

    logging.debug("[*] Done")

    # if text != "Occupied":
    firstFrame = gray

    # draw the text and timestamp on the frame
    cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(frame, datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    # show the frame and record if the user presses a key
    # cv2.imshow("Security Feed", frame)
    # cv2.imshow("Thresh", thresh)
    # cv2.imshow("Frame Delta", frameDelta)

    if text == "Occupied":
        logging.debug("[+] Writing image to file...")

        cv2.imwrite(os.path.join(IMAGES_DIR, f'{datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}_office.png'), frame)
        logging.debug("[*] Done")

    key = cv2.waitKey(1) & 0xFF
    # if the `q` key is pressed, break from the lop
    if key == ord("q"):
        break

clean_cv()

logging.info("[*] Exiting.")