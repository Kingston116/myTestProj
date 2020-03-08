import time
from collections import deque
import numpy as np
import argparse
import cv2
import imutils
import logging
from pyzbar import pyzbar
import threading

class Camera:
    def __init__(self):
        # Set channels to the number of servo channels on your kit.
        # 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
        self.blue = 27
        self.green = 61
        self.red = 114
        self.color_lower, self.color_upper = self.get_colour_bound()
        self.camera = cv2.VideoCapture(0)
        self.frame=None
        self.x = 0
        self.y = 0
    
    def show_image(self):
        # show the frame to our screen
        while True:
            if self.frame is not None:
                cv2.imshow("Frame", self.frame)
                key = cv2.waitKey(1) & 0xFF
                time.sleep(0.3)
            

    def get_colour_bound(self):
        color = np.uint8([[[self.blue, self.green, self.red]]])
        hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)

        hue = hsv_color[0][0][0]
        color_lower = np.array([hue - 10, 100, 100], dtype=np.uint8)
        color_upper = np.array([hue + 10, 255, 255], dtype=np.uint8)
        print("Lower bound is :{0}".format(color_lower))
        print("Upper bound is :{0}".format(color_upper))
        return color_lower, color_upper
    
    def get_barcode(self):        
        (grabbed, self.frame) = self.camera.read()
        barcodes = pyzbar.decode(self.frame)
        logging.debug(barcodes)
        return barcodes

    def check_object(self):
        
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
        # grab the current frame
        (grabbed, self.frame) = self.camera.read()

        # resize the frame, inverted ("vertical flip" w/ 180degrees),
        # blur it, and convert it to the HSV color space
        self.frame = imutils.resize(self.frame, width=600)
        self.frame = imutils.rotate(self.frame, angle=180)
        # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
        
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)

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
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 20:
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(self.frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(self.frame, center, 5, (0, 0, 255), -1)
            else:
                self.x = -1
                self.y = -1
        else:
            self.x = -1
            self.y = -1
        cv2.imshow("Frame", self.frame)
        key = cv2.waitKey(1) & 0xFF
        return self.x, self.y

    def camera(self):


        # if a video path was not supplied, grab the reference
        # to the webcam

        # keep looping
        self.check_object()

        # cleanup the camera and close any open windows
        # camera.release()
        # cv2.destroyAllWindows()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
