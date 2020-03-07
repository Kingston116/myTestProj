import logging
import time

import RPi.GPIO as GPIO


class Ultrasonic:
    def __init__(self):
        self.z = 0
        # set GPIO Pins
        self.GPIO_TRIGGER = 18
        self.GPIO_ECHO = 24
        # set GPIO direction (IN / OUT)
        GPIO.setup(self.GPIO_TRIGGER, GPIO.OUT)
        GPIO.setup(self.GPIO_ECHO, GPIO.IN)

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

    def get_distance(self):
        try:
            while True:
                self.z = self.distance()
                logging.debug('Distance {0}'.format(self.z))
                time.sleep(0.1)

            # Reset by pressing CTRL + C
        except KeyboardInterrupt:
            logging.debug("Measurement stopped by User")
            GPIO.cleanup()

    def calculate_zaxis(self):
        return int(1.3 * self.z * 2.7)
