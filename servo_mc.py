import time
from collections import deque
import numpy as np
import argparse
import cv2
import threading
import imutils
import logging
from pyzbar import pyzbar


class Camera:
    def __init__(self):
        # Set channels to the number of servo channels on your kit.
        # 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
        self.blue = 34
        self.green = 54
        self.red = 0
        self.color_lower, self.color_upper = self.get_colour_bound()
        self.camera = cv2.VideoCapture(0)

    def get_colour_bound(self):
        color = np.uint8([[[self.blue, self.green, self.red]]])
        hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)

        hue = hsv_color[0][0][0]
        color_lower = (hue - 10, 100, 100)
        color_upper = (hue + 10, 255, 255)
        print("Lower bound is :{0}".format(color_lower))
        print("Upper bound is :{0}".format(color_upper))
        return color_lower, color_upper

    def check_object(self):
        # grab the current frame
        (grabbed, frame) = self.camera.read()
        barcodes = pyzbar.decode(frame)
        logging.debug(barcodes)

        # resize the frame, inverted ("vertical flip" w/ 180degrees),
        # blur it, and convert it to the HSV color space
        frame = imutils.resize(frame, width=600)
        frame = imutils.rotate(frame, angle=180)
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # construct a mask for the color "green", then perform
        # a series of dilations and erosions to remove any small
        # blobs left in the mask
        mask = cv2.inRange(hsv, self.color_lower, self.color_upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)

        # find contours in the mask and initialize the current
        # (x, y) center of the ball
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None

        # only proceed if at least one contour was found
        if len(cnts) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            # print((x,y))
            logging.debug('Camera : {0}'.format((x, y)))
            self.x = x
            self.y = y
        else:
            self.x = -1
            self.y = -1

        # show the frame to our screen
        cv2.imshow("Frame", frame)

    def camera(self):

        # construct the argument parse and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-v", "--video",
                        help="path to the (optional) video file")
        ap.add_argument("-b", "--buffer", type=int, default=64,
                        help="max buffer size")
        args = vars(ap.parse_args())

        # define the lower and upper boundaries of the "yellow object"
        # (or "ball") in the HSV color space, then initialize the
        # list of tracked points

        pts = deque(maxlen=args["buffer"])

        # if a video path was not supplied, grab the reference
        # to the webcam

        # keep looping
        self.check_object()

        # cleanup the camera and close any open windows
        #camera.release()
        #cv2.destroyAllWindows()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

