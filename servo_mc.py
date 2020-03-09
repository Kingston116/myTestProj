import logging
import threading
import time

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

        self.Y_limit = {"Lower": 360, "Upper": 363}
        self.X_limit = {"Lower": 324, "Upper": 326}

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
                    TXAxis = threading.Thread(target=self.adjust_x_axis)
                    TXAxis.start()
                    logging.debug('Start X')

                    TYAxis = threading.Thread(target=self.adjust_y_axis)
                    TYAxis.start()
                    logging.debug('Start Y')
                    while not self.xComplete or not self.yComplete:
                        continue
                    self.adjust_z_axis()
                    return

    @staticmethod
    def get_increment_value(value, value_limit):
        if value > (value_limit - 40):
            increment_value = 2
        else:
            increment_value = 0.05
        return increment_value

    @staticmethod
    def get_decrement_value(value, value_limit):
        if value < (value_limit - 40):
            decrement_value = 2
        else:
            decrement_value = 0.05
        return decrement_value

    def adjust_y_axis(self):
        rotate_first_elbow_angle = self.kit.servo[1].angle
        try:
            while True:
                y = self.y
                logging.debug('Y adjust {0}'.format(["Y Coord", y]))
                if y in range(self.Y_limit['Lower'], self.Y_limit['Upper']) and \
                        self.x in range(self.X_limit['Lower'], self.X_limit['Upper']):
                    self.yValue = rotate_first_elbow_angle
                    break
                while y > self.Y_limit['Upper'] and rotate_first_elbow_angle < 100:
                    rotate_first_elbow_angle = rotate_first_elbow_angle + \
                                               self.get_increment_value(y, self.Y_limit['Upper'])
                    self.kit.servo[1].angle = rotate_first_elbow_angle
                    logging.debug('Y adjust {0}'.format(["Y", rotate_first_elbow_angle, y]))
                    self.check_object()
                    y = self.y
                while y < self.Y_limit['Lower'] and rotate_first_elbow_angle > 15:

                    rotate_first_elbow_angle = rotate_first_elbow_angle - \
                                               self.get_decrement_value(y, self.Y_limit['Lower'])
                    self.kit.servo[1].angle = rotate_first_elbow_angle
                    logging.debug('Y adjust {0}'.format(["Y", rotate_first_elbow_angle, y]))
                    self.check_object()
                    y = self.y
                time.sleep(1)
        except KeyboardInterrupt:
            print("except")
        finally:
            print("finally")
            self.rotateFistElbowAngle = rotate_first_elbow_angle
            self.xComplete = True
        time.sleep(2)

    def adjust_x_axis(self):
        rotate_base_angle = self.kit.servo[2].angle
        try:
            while True:
                x = self.x
                logging.debug('X adjust {0}'.format(["X Coord", x]))
                # print(["X Coord", x])
                if x in range(self.X_limit['Lower'], self.X_limit['Upper']) and \
                        self.y in range(self.Y_limit['Lower'], self.Y_limit['Upper']):
                    self.xValue = rotate_base_angle
                    break
                time.sleep(2)

                while x > self.X_limit['Upper'] and rotate_base_angle > 45:
                    rotate_base_angle = rotate_base_angle - self.get_increment_value(x, self.X_limit['Upper'])
                    self.kit.servo[2].angle = rotate_base_angle
                    logging.debug('X adjust {0}'.format(["X", rotate_base_angle, x]))
                    self.check_object()
                    x = self.x
                while x < self.X_limit['Lower'] and rotate_base_angle < 130:
                    rotate_base_angle = rotate_base_angle + self.get_decrement_value(x, self.X_limit['Lower'])
                    self.kit.servo[2].angle = rotate_base_angle
                    logging.debug('X adjust {0}'.format(["X", rotate_base_angle, x]))
                    self.check_object()
                    x = self.x
                time.sleep(1)
        except KeyboardInterrupt:
            print("except")
        finally:
            print("finally")
            self.rotateAngle = rotate_base_angle
            self.yComplete = True
        time.sleep(2)

    def adjust_z_axis(self):
        z = self.ultrasonic.get_distance()
        try:
            while z > 3.5:
                self.robot.get_current_coord()
                self.kit.servo[5].angle = self.kit.servo[5].angle - 1
                self.kit.servo[1].angle = self.kit.servo[1].angle + 0.16
                time.sleep(0.1)
                z = self.ultrasonic.get_distance()
        except KeyboardInterrupt:
            print("except")
        finally:
            print("finally")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    servoObj = servo()
    servoObj.kit.servo[4].angle = 110
    time.sleep(0.2)
    servoObj.robot.robot_coord((90, 130, 120, 30, 90, 90))
    time.sleep(0.2)
    servoObj.findAngle()
    coord = servoObj.robot.get_current_coord()
    new_coord = (coord[0], coord[1] - 12, coord[2], coord[3], coord[4], coord[5])
    servoObj.robot.robot_coord(new_coord)
    new_coord = (coord[0], coord[1], coord[2], coord[3], coord[4], coord[5])
    servoObj.robot.robot_coord(new_coord)
