import logging
import threading
import time

import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit

from Camera import Camera
from robot import Robot
from ultrasonic import Ultrasonic


class servo():
    def __init__(self):
        # Set channels to the number of servo channels on your kit.
        # 8 for FeatherWing, 16 for Shield/HAT/Bonnet.
        self.kit = ServoKit(channels=16)
        logging.debug('Setting channel to 16')
        self.z = 0
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
        self.camera = Camera()
        self.robot = Robot()
        self.ultrasonic = Ultrasonic()

    def check_object(self):
        self.x, self.y = self.camera.check_object()
        return self.x, self.y

    def get_current_coord(self):
        current_coord = (round(self.kit.servo[2].angle),
                         round(self.kit.servo[5].angle),
                         round(self.kit.servo[4].angle),
                         round(self.kit.servo[1].angle),
                         round(self.kit.servo[0].angle),
                         round(self.kit.servo[3].angle))
        return current_coord

    def findAngle(self):
        counter = 0
        current_coord = self.get_current_coord()

        self.x, self.y = self.check_object()
        for base_list in self.robot.list_coord:
            list_coord = self.robot.dict_coord[str(base_list)]
            for new_coord in list_coord:
                if self.y is -1 or self.x is -1:
                    self.robot.move_to_coord(current_coord, new_coord)
                    self.check_object()
                    current_coord = new_coord
                    counter += 1
                else:                    
                    self.check_object()
                    #self.camera.get_barcode()
                    TXAxis = threading.Thread(target=self.adjustXAxis)
                    TXAxis.start()
                    logging.debug('Start X')

                    TYAxis = threading.Thread(target=self.adjustYAxis)
                    TYAxis.start()
                    logging.debug('Start Y')
                    while not self.xComplete or not self.yComplete:
                        continue
                    self.adjustZAxis()
                    return
                    '''
                    TMove = threading.Thread(target=self.movementLoop)
                    TMove.start()'''

    def adjustYAxis(self):
        rotateFistElbowAngle = self.kit.servo[1].angle
        try:
            while True:
                y = self.y
                logging.debug('Y adjust {0}'.format(["Y Coord", y]))
                if 363 >= y >= 360 and 326 >= self.x >= 324:
                    # rotateFistElbowAngle = 45
                    self.yValue = rotateFistElbowAngle
                    break
                while y > 363 and rotateFistElbowAngle < 100:
                    
                    rotateFistElbowAngle = rotateFistElbowAngle + 0.05
                    self.kit.servo[1].angle = rotateFistElbowAngle
                    # print(["Y", rotateFistElbowAngle, y])
                    logging.debug('Y adjust {0}'.format(["Y", rotateFistElbowAngle, y]))
                    self.check_object()
                    y = self.y
                while y < 360 and rotateFistElbowAngle > 15:
                    
                    rotateFistElbowAngle = rotateFistElbowAngle - 0.05
                    self.kit.servo[1].angle = rotateFistElbowAngle
                    # print(["Y", rotateFistElbowAngle, y])
                    logging.debug('Y adjust {0}'.format(["Y", rotateFistElbowAngle, y]))
                    self.check_object()
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
        rotateAngle = self.kit.servo[2].angle
        rotateFistElbowAngle = self.kit.servo[1].angle
        try:
            while True:
                x = self.x
                logging.debug('X adjust {0}'.format(["X Coord", x]))
                # print(["X Coord", x])
                if 326 >= x >= 324 and 363 >= self.y >= 360:
                    # rotateAngle = 90
                    self.xValue = rotateAngle
                    break
                time.sleep(2)

                while x > 326 and rotateAngle > 45:
                    rotateAngle = rotateAngle - 0.05
                    self.kit.servo[2].angle = rotateAngle
                    # print(["X", rotateAngle, x])
                    logging.debug('X adjust {0}'.format(["X", rotateAngle, x]))
                    self.check_object()
                    x = self.x
                while x < 324 and rotateAngle < 130:
                    rotateAngle = rotateAngle + 0.05
                    self.kit.servo[2].angle = rotateAngle
                    logging.debug('X adjust {0}'.format(["X", rotateAngle, x]))
                    self.check_object()
                    x = self.x
                time.sleep(1)
        except KeyboardInterrupt:
            print("except")
        finally:
            print("finally")
            self.rotateAngle = rotateAngle
            self.yComplete = True
        time.sleep(2)
    
    def adjustZAxis(self):
        rotateAngle = self.kit.servo[5].angle
        rotateFistElbowAngle = self.kit.servo[1].angle
        z = self.ultrasonic.get_distance()
        try:
            while z > 3.5:
                self.robot.get_current_coord()
                rotateAngle = rotateAngle - 1
                self.kit.servo[5].angle = rotateAngle
                rotateFistElbowAngle = rotateFistElbowAngle + 0.16
                self.kit.servo[1].angle = rotateFistElbowAngle
                time.sleep(0.1)
                z = self.ultrasonic.get_distance()
        except KeyboardInterrupt:
            print("except")
        finally:
            print("finally")
                
    def moveXrapid(self, x):
        self.kit.servo[2].angle = x
        time.sleep(0.2)

    def moveYrapid(self, y):
        self.kit.servo[1].angle = y
        time.sleep(0.2)

    def moveZrapid(self, z1, z2):
        time.sleep(0.2)
        y5 = 90 - z1
        self.kit.servo[5].angle = y5
        logging.debug('Y AXIS : {0} Z AXIS :{1}'.format(self.yValue, z1))
        if self.yValue - z1 < 0:
            # self.kit.servo[1].angle = 0
            z1 = 0
        else:
            self.kit.servo[1].angle = self.yValue - z1
        time.sleep(0.2)
        self.kit.servo[5].angle = y5 - 10
        time.sleep(0.2)
        self.kit.servo[5].angle = y5
        # self.kit.servo[1].angle = self.yValue+z1

    def movementLoop(self):
        try:
            # print("position")
            Zx = threading.Thread(target=self.ultrasonic.getDistance)
            Zx.start()
            logging.debug('Movement Position')
            counter = 0
            zValue = self.ultrasonic.calculateZaxis()
            while True:
                logging.debug('Z Value : {0}'.format(zValue))
                if counter % 2 == 0:
                    RXAxis = threading.Thread(target=self.moveXrapid, args=(90,))
                    RXAxis.start()
                    RYAxis = threading.Thread(target=self.moveYrapid, args=(45,))
                    # RYAxis.start()
                    RZAxis = threading.Thread(target=self.moveZrapid, args=(zValue, 90,))
                    RZAxis.start()
                else:
                    RXAxis = threading.Thread(target=self.moveXrapid, args=(self.rotateAngle,))
                    RXAxis.start()
                    RYAxis = threading.Thread(target=self.moveYrapid, args=(self.rotateFistElbowAngle,))
                    # RYAxis.start()
                    RZAxis = threading.Thread(target=self.moveZrapid, args=(zValue, 90,))
                    RZAxis.start()
                time.sleep(0.6)
                counter += 1
        except KeyboardInterrupt:
            print("except")
        finally:
            print("finally")
        time.sleep(2)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    servoObj = servo()

    # Base
    # servoObj.kit.servo[2].angle = 90
    # time.sleep(0.2)
    # Twist wrist
    # servoObj.kit.servo[0].angle = 90
    # time.sleep(0.2)
    # Arm
    # servoObj.kit.servo[5].angle = 120
    # time.sleep(0.2)
    # time.sleep(15)
    servoObj.kit.servo[4].angle = 110
    time.sleep(0.2)
    servoObj.robot.robot_coord((90, 130, 120, 30, 90, 90))
    time.sleep(0.2)
    servoObj.findAngle()
    servoObj.adjustXAxis()
    servoObj.adjustYAxis()
    coord = servoObj.robot.get_current_coord()
    new_coord = (coord[0],coord[1]-12,coord[2], coord[3],coord[4],coord[5])
    servoObj.robot.robot_coord(new_coord)
    new_coord = (coord[0],coord[1],coord[2], coord[3],coord[4],coord[5])
    servoObj.robot.robot_coord(new_coord)
    # time.sleep(0.2)
    # servoObj.kit.servo[1].angle = 20
    # time.sleep(0.2)
    # servoObj.kit.servo[3].angle = 135
    # servoObj.kit.servo[0].angle = 70
    '''servoObj.robot.robot_coord((84, 61, 120, 46, 90, 90))
    time.sleep(0.2)
    servoObj.robot.robot_coord((87, 61, 120, 40, 90, 90))
    time.sleep(0.2)
    servoObj.robot.robot_coord((87, 47, 120, 40, 90, 90))
    time.sleep(0.2)
    servoObj.robot.robot_coord((84, 61, 120, 40, 90, 90))
    print(servoObj.check_object())'''
