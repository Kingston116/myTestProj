import RPi.GPIO as GPIO
import time
import sys
from collections import deque
import numpy as np
import argparse
import cv2
import threading
import imutils
from adafruit_servokit import ServoKit
import adafruit_pca9685
import busio
import board
import logging
import pdb
from pyzbar import pyzbar

class servo():
    def __init__(self):
        # Set channels to the number of servo channels on your kit.
        # 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
        
        #i2c = busio.I2C(board.SCL, board.SDA)
        #pca = adafruit_pca9685.PCA9685(i2c)
        #pca.frequency = 50
        self.kit = ServoKit(channels=16)
        logging.debug('Setting channel to 16')
        #set GPIO Pins
        self.GPIO_TRIGGER = 18
        self.GPIO_ECHO = 24
        self.z = 0
        #set GPIO direction (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)
        logging.debug('Set to 90 degree')
        time.sleep(5)
        self.x = 0
        self.y = 0
        self.xValue = 0
        self.yValue = 0
        self.rotateFistElbowAngle = 0
        self.rotateAngle = 0
        self.xComplete = False
        self.yComplete = False
        self.list_coord = [45, 90, 135]
        self.dict_coord = {"45": [(45, 125, 110, 35, 135, 45),
                                  (45, 120, 115, 40, 133, 46),
                                  (45, 115, 120, 45, 131, 47),
                                  (45, 110, 125, 50, 128, 49),
                                  (45, 105, 130, 55, 126, 50),
                                  (45, 100, 135, 60, 124, 52),
                                  (45, 95, 140, 65, 122, 53),
                                  (45, 90, 145, 70, 120, 54),
                                  (45, 85, 150, 75, 118, 56),
                                  (45, 80, 155, 80, 116, 57),
                                  (45, 75, 160, 85, 114, 58),
                                  (45, 70, 165, 90, 111, 60)],
                           "90": [(90, 130, 90, 30, 90, 90),
                                  (90, 125, 110, 35, 90, 90),
                                  (90, 120, 115, 40, 90, 90),
                                  (90, 115, 120, 45, 90, 90),
                                  (90, 110, 125, 50, 90, 90),
                                  (90, 105, 130, 55, 90, 90),
                                  (90, 100, 135, 60, 90, 90),
                                  (90, 95, 140, 65, 90, 90),
                                  (90, 90, 145, 70, 90, 90),
                                  (90, 85, 150, 75, 90, 90),
                                  (90, 80, 155, 80, 90, 90),
                                  (90, 75, 160, 85, 90, 90),
                                  (90, 70, 165, 90, 90, 90)],
                           "135": [(135, 125, 130, 35, 45, 135),
                                   (135, 120, 135, 40, 47, 134),
                                   (135, 115, 120, 45, 49, 133),
                                   (135, 110, 125, 50, 51, 131),
                                   (135, 105, 130, 55, 53, 130),
                                   (135, 100, 135, 60, 55, 128),
                                   (135, 95, 140, 65, 57, 127),
                                   (135, 90, 145, 70, 59, 126),
                                   (135, 85, 150, 75, 61, 124),
                                   (135, 80, 155, 80, 63, 123),
                                   (135, 75, 160, 85, 66, 122),
                                   (135, 70, 165, 90, 70, 120)],
                           }
    
    def distance(self):
        # set Trigger to HIGH
        GPIO.output(self.GPIO_TRIGGER, True)
     
        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.GPIO_TRIGGER, False)
     
        StartTime = time.time()
        StopTime = time.time()
     
        # save StartTime
        while GPIO.input(self.GPIO_ECHO) == 0:
            StartTime = time.time()
     
        # save time of arrival
        while GPIO.input(self.GPIO_ECHO) == 1:
            StopTime = time.time()
     
        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        distance = (TimeElapsed * 34300) / 2
     
        return distance
    
    def getDistance(self):
        try:
            while True:
                self.z = self.distance()
                logging.debug('Distance {0}'.format(self.z))
                time.sleep(0.1)
     
            # Reset by pressing CTRL + C
        except KeyboardInterrupt:
            logging.debug("Measurement stopped by User")
            GPIO.cleanup()
    
    def setZAxis(self, z1, z2):
        
        try:
          time.sleep(0.5)
          self.SetAngle(z1, self.p)
          print(z1)
          time.sleep(0.5)
          self.SetAngle(z2, self.p)
          print(z2)
          time.sleep(0.5)
        except KeyboardInterrupt:
          print("except")
          p.stop()
          GPIO.cleanup()
        finally:
          print("finally")
        
    def SetAngle(self, angle, p):
        duty = (angle / 18 + 2)
        p.ChangeDutyCycle(duty)
        time.sleep(0.05)
        p.ChangeDutyCycle(0)
        
    def camera(self):
        blue = 34
        green = 54
        red = 0
        color = np.uint8([[[blue, green, red]]])
        hsv_color = cv2.cvtColor(color, cv2.COLOR_BGR2HSV)
         
        hue = hsv_color[0][0][0]
        print(hsv_color)
        print("Lower bound is :"),
        print("[" + str(hue-10) + ", 100, 100]\n")
         
        print("Upper bound is :"),
        print("[" + str(hue + 10) + ", 255, 255]")



        # Read the picure - The 1 means we want the image in BGR
        img = cv2.imread('/home/pi/green.png', 1) 

        # resize imag to 20% in each axis
        img = cv2.resize(img, (0,0), fx=0.2, fy=0.2)
        # convert BGR image to a HSV image
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) 

        # NumPy to create arrays to hold lower and upper range 
        # The dtype = np.uint8 means that data type is an 8 bit integer

        lower_range = np.array([69, 100, 100], dtype=np.uint8) 
        upper_range = np.array([89, 255, 255], dtype=np.uint8)

        # create a mask for image
        mask = cv2.inRange(hsv, lower_range, upper_range)

        # display both the mask and the image side-by-side
        cv2.imshow('mask',mask)
        cv2.imshow('image', img)

        # wait to user to press [ ESC ]
        #while(1):
        #  k = cv2.waitKey(0)
        #  if(k == 27):
        #    break
         
        cv2.destroyAllWindows()

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
        colorLower = (69, 100, 100)
        colorUpper = (89, 255, 255)
        pts = deque(maxlen=args["buffer"])
         
        # if a video path was not supplied, grab the reference
        # to the webcam
        if not args.get("video", False):
                camera = cv2.VideoCapture(0)
         
        # otherwise, grab a reference to the video file
        else:
                camera = cv2.VideoCapture(args["video"])
        # keep looping
        while True:
                # grab the current frame
                (grabbed, frame) = camera.read()
                #barcodes = pyzbar.decode(frame)
                #logging.debug (barcodes)
         
                # resize the frame, inverted ("vertical flip" w/ 180degrees),
                # blur it, and convert it to the HSV color space
                frame = imutils.resize(frame, width=600)
                frame = imutils.rotate(frame, angle=180)
                # blurred = cv2.GaussianBlur(frame, (11, 11), 0)
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
         
                # construct a mask for the color "green", then perform
                # a series of dilations and erosions to remove any small
                # blobs left in the mask
                mask = cv2.inRange(hsv, colorLower, colorUpper)
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
                        #print((x,y))
                        logging.debug('Camera : {0}'.format((x,y)))
                        self.x = x
                        self.y = y
                        M = cv2.moments(c)
                        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
         
                        # only proceed if the radius meets a minimum size
                        if radius > 10:
                                # draw the circle and centroid on the frame,
                                # then update the list of tracked points
                                cv2.circle(frame, (int(x), int(y)), int(radius),
                                        (0, 255, 255), 2)
                                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                else:
                    self.x = -1
                    self.y = -1
         
                # update the points queue
                pts.appendleft(center)
                
                        # loop over the set of tracked points
                for i in range(1, len(pts)):
                        # if either of the tracked points are None, ignore
                        # them
                        if pts[i - 1] is None or pts[i] is None:
                                continue
         
                        # otherwise, compute the thickness of the line and
                        # draw the connecting lines
                        thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
                        cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
         
                # show the frame to our screen
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF
         
     
        # cleanup the camera and close any open windows
        camera.release()
        cv2.destroyAllWindows()
              
    def findButtonAngle(self):  
        
        rotateAngle = 90
        rotateFistElbowAngle = 45
        time.sleep(1)
        #self.kit.servo[0].angle = rotateFistElbowAngle
        time.sleep(0.5)
        self.kit.servo[1].angle = rotateAngle
        time.sleep(5)
        try:
          while True:
            y = self.y
            x = self.x
            print(["Coord", x , y])
            if x < 350 and x > 250 and y < 300 and y > 200:
                break
            
            time.sleep(2)
            while y > 300:
                rotateFistElbowAngle = rotateFistElbowAngle + 0.5
                self.kit.servo[3].angle = rotateFistElbowAngle
                print(["Y", rotateFistElbowAngle, y])
                time.sleep(0.1)
                y = self.y
                x = self.x
                
            while y < 200:
                rotateFistElbowAngle = rotateFistElbowAngle - 0.5
                self.kit.servo[3].angle = rotateFistElbowAngle
                print(["Y", rotateFistElbowAngle, y])
                time.sleep(0.1)
                y = self.y
                x = self.x
            
            while x > 350:
                rotateAngle = rotateAngle - 0.5
                self.kit.servo[6].angle = rotateAngle
                print(["X", rotateAngle, x])
                time.sleep(0.1)
                
                y = self.y
                x = self.x
            while x < 250:
                rotateAngle = rotateAngle - 0.5
                self.kit.servo[6].angle = rotateAngle
                print(["X", rotateAngle, x])
                time.sleep(0.1)
                
                y = self.y
                x = self.x
                
            '''while y == -1:
                rotateFistElbowAngle = rotateFistElbowAngle - 1
                if rotateFistElbowAngle < 15:
                    rotateFistElbowAngle = 70
                self.kit.servo[3].angle = rotateFistElbowAngle
                print(["Y-Rebound", rotateFistElbowAngle, y])
                time.sleep(0.25)
                y = self.y
                x = self.x
                
            while x == -1 :
                rotateAngle = rotateAngle + 1
                self.kit.servo[6].angle = rotateAngle
                print(["X-Rebound", rotateAngle, x])
                time.sleep(0.25)
                y = self.y
                x = self.x'''
                
            
            time.sleep(1)
        except KeyboardInterrupt:
          print("except")
        finally:
          print("finally")
        time.sleep(2)
        
    def get_current_coord(self):
        current_coord = (round(self.kit.servo[2].angle),
                                         round(self.kit.servo[5].angle),
                                         round(self.kit.servo[4].angle),
                                         round(self.kit.servo[1].angle),
                                         round(self.kit.servo[0].angle),
                                         round(self.kit.servo[3].angle))
        return current_coord
        
    def findAngle(self):
        #self.kit.servo[1].angle = 45
        #time.sleep(0.3)
        counter = 0        
        current_coord = self.get_current_coord()
        
        for base_list in self.list_coord:
            list_coord = self.dict_coord[str(base_list)]
            if self.y is -1 or self.x is -1:
                for new_coord in list_coord:
                    #new_coord = (135, 70, 160, 92, 90, 80)
                    self.move_to_coord(current_coord, new_coord)
                    current_coord = new_coord
                    counter += 1
                
        TXAxis = threading.Thread(target=self.adjustXAxis)
        #TXAxis.start()
        logging.debug('Start X')
        
        TYAxis = threading.Thread(target=self.adjustYAxis)
        #TYAxis.start()
        logging.debug('Start Y')
        while not self.xComplete or not self.yComplete:
            continue
        '''
        TMove = threading.Thread(target=self.movementLoop)
        TMove.start()'''
    def move_to_coord(self, current_coord, new_coord):
        logging.debug("Current : {0}".format(current_coord))
        # base_angle = min(list_coord, key=lambda c: (c - round(self.kit.servo[2].angle)) ** 2)
        base_angle = min(self.list_coord, key=lambda list_value: abs(list_value - current_coord[0]))
        logging.debug("Current base: {0}".format(base_angle))
        closest = self.closest_coord(base_angle, current_coord)
        logging.debug("closest : {0}".format(closest))
        closest_new_coord = self.closest_coord(new_coord[0], new_coord)

        list_coord = self.dict_coord[str(closest[0])]
        current_index = list_coord.index(closest)
        if str(new_coord[0]) != str(closest[0]):
            for i in range(current_index, -1, -1):
                self.robot_coord(list_coord[i])
            list_coord = self.dict_coord[str(new_coord[0])]
            expected_index = list_coord.index(closest_new_coord)
            for i in range(0, expected_index+1):
                self.robot_coord(list_coord[i])
        else:
            expected_index = list_coord.index(closest_new_coord)
            for i in range(current_index, expected_index+1):
                self.robot_coord(list_coord[i])

        if closest_new_coord != new_coord:
            logging.debug("Additional movement to : {0}".format(new_coord))

    def closest_coord(self, base_angle, coord):
        return min(self.dict_coord[str(base_angle)], key=lambda c: (c[0] - coord[0]) ** 2 +
                                                                      (c[1] - coord[1]) ** 2 +
                                                                      (c[2] - coord[2]) ** 2 +
                                                                      (c[3] - coord[3]) ** 2 +
                                                                      (c[4] - coord[4]) ** 2 +
                                                                      (c[5] - coord[5]) ** 2)

    def robot_coord(self, coord):
        
        self.kit.servo[2].angle = coord[0]
        self.kit.servo[5].angle = coord[1]
        self.kit.servo[4].angle = coord[2]
        self.kit.servo[1].angle = coord[3]
        self.kit.servo[0].angle = coord[4]
        self.kit.servo[3].angle = coord[5]
        
        logging.debug("Moved to : {0}".format(coord))
        time.sleep(0.3)
        
    def adjustYAxis(self):
        rotateFistElbowAngle = 45
        self.kit.servo[1].angle = rotateFistElbowAngle
        time.sleep(5)
        try:
          while True:
            y = self.y
            logging.debug('Y adjust {0}'.format(["Y Coord", y]))
            if 300 > y > 200:
                #rotateFistElbowAngle = 45
                self.yValue = rotateFistElbowAngle
                break
            while y > 300 and rotateFistElbowAngle < 100:
                rotateFistElbowAngle = rotateFistElbowAngle + 1
                self.kit.servo[1].angle = rotateFistElbowAngle
                #print(["Y", rotateFistElbowAngle, y])
                logging.debug('Y adjust {0}'.format(["Y", rotateFistElbowAngle, y]))
                time.sleep(0.3)
                y = self.y
            while y < 200 and rotateFistElbowAngle > 15:
                rotateFistElbowAngle = rotateFistElbowAngle - 1
                self.kit.servo[1].angle = rotateFistElbowAngle
                #print(["Y", rotateFistElbowAngle, y])
                logging.debug('Y adjust {0}'.format(["Y", rotateFistElbowAngle, y]))
                time.sleep(0.3)
                y = self.y
            time.sleep(1)
        except KeyboardInterrupt:
          print("except")
        finally:
          print("finally")
          self.rotateFistElbowAngle = rotateFistElbowAngle
          self.xComplete = True
        time.sleep(2)
        
    def adjustXAxis(self):
        rotateAngle = 90
        time.sleep(1)
        self.kit.servo[2].angle = rotateAngle
        time.sleep(5)
        try:
          while True:
            x = self.x
            logging.debug('X adjust {0}'.format(["X Coord", x]))
            #print(["X Coord", x])
            if  350 > x > 250:
                #rotateAngle = 90
                self.xValue = rotateAngle
                break
            time.sleep(2)
            
            while x > 350 and rotateAngle > 45:
                rotateAngle = rotateAngle - 1
                self.kit.servo[2].angle = rotateAngle
                #print(["X", rotateAngle, x])
                logging.debug('X adjust {0}'.format(["X", rotateAngle, x]))
                time.sleep(0.3)
                x = self.x
            while x < 250 and rotateAngle < 130:
                rotateAngle = rotateAngle + 1
                self.kit.servo[2].angle = rotateAngle
                logging.debug('X adjust {0}'.format(["X", rotateAngle, x]))
                time.sleep(0.3)
                x = self.x   
            time.sleep(1)
        except KeyboardInterrupt:
          print("except")
        finally:
          print("finally")
          self.rotateAngle = rotateAngle
          self.yComplete = True
        time.sleep(2)
        
    def moveXrapid(self, x):
        self.kit.servo[2].angle = x
        time.sleep(0.2)
        
    def moveYrapid(self, y):
        self.kit.servo[1].angle = y
        time.sleep(0.2)
        
    def moveZrapid(self, z1, z2):
        time.sleep(0.2)
        y5 = 90-z1
        self.kit.servo[5].angle = y5
        logging.debug('Y AXIS : {0} Z AXIS :{1}'.format(self.yValue, z1))
        if self.yValue-z1 < 0:
            #self.kit.servo[1].angle = 0
            z1 = 0
        else:
            self.kit.servo[1].angle = self.yValue-z1
        time.sleep(0.2)        
        self.kit.servo[5].angle = y5-10
        time.sleep(0.2)        
        self.kit.servo[5].angle = y5
        #self.kit.servo[1].angle = self.yValue+z1
        
    def calculateZaxis(self):
        return int(1.3 * self.z * 2.7)
    
    def movementLoop(self):
        try:
          #print("position")
          Zx = threading.Thread(target=self.getDistance)
          Zx.start()
          logging.debug('Movement Position')
          counter = 0
          self.pin = 19
          GPIO.setmode(GPIO.BCM)
          GPIO.setup(self.pin, GPIO.OUT)
          self.p = GPIO.PWM(self.pin, 60) # GPIO 17 for PWM with 50Hz        
          self.p.start(2.5) # Initialization
          logging.debug('Initiate PWM for motor 3')
          self.SetAngle(90, self.p)
          zValue = self.calculateZaxis()
          while True:
            logging.debug('Z Value : {0}'.format(zValue))
            if counter % 2 == 0:
                RXAxis = threading.Thread(target=self.moveXrapid, args=(90,))
                RXAxis.start()
                RYAxis = threading.Thread(target=self.moveYrapid, args=(45,))
                #RYAxis.start()
                RZAxis = threading.Thread(target=self.moveZrapid, args=(zValue,90,))
                RZAxis.start()
            else:
                RXAxis = threading.Thread(target=self.moveXrapid, args=(self.rotateAngle,))
                RXAxis.start()
                RYAxis = threading.Thread(target=self.moveYrapid, args=(self.rotateFistElbowAngle,))
                #RYAxis.start()
                RZAxis = threading.Thread(target=self.moveZrapid, args=(zValue,90,))
                RZAxis.start()
            time.sleep(0.6)
            counter += 1
        except KeyboardInterrupt:
          print("except")
        finally:
          print("finally")
        time.sleep(2)
        
            
if __name__=="__main__":
    
    logging.basicConfig(level=logging.DEBUG)
    servoObj = servo()
    
    Tx = threading.Thread(target=servoObj.camera)
    Tx.start()
    #Base
    #servoObj.kit.servo[2].angle = 90
    #time.sleep(0.2)
    #Twist wrist
    #servoObj.kit.servo[0].angle = 90
    #time.sleep(0.2)
    #Arm
    #servoObj.kit.servo[5].angle = 120
    #time.sleep(0.2)
    time.sleep(15)
    servoObj.findAngle()
    #servoObj.kit.servo[4].angle = 160
    #time.sleep(0.2)
    #servoObj.kit.servo[1].angle = 20
    #time.sleep(0.2)
    #servoObj.kit.servo[3].angle = 135
    #servoObj.kit.servo[0].angle = 70
    #servoObj.robot_coord((135, 125, 130, 35, 10, 180))
    #servoObj.robot_coord((135, 115, 120, 45, 20, 180))
    print(servoObj.get_current_coord())
    
