import logging
import sys
from time import sleep

logging.basicConfig(level=logging.DEBUG)


class Robot:
    def __init__(self):
        self.y = -1
        self.x = -1
        self.list_coord = [45, 90, 135]
        self.dict_coord = {"45": [(45, 125, 110, 35, 90, 90),
                                  (45, 120, 115, 40, 90, 90),
                                  (45, 115, 120, 45, 90, 90),
                                  (45, 110, 125, 50, 90, 90),
                                  (45, 105, 130, 55, 90, 90),
                                  (45, 100, 135, 60, 90, 90),
                                  (45, 95, 140, 65, 90, 90),
                                  (45, 90, 145, 70, 90, 90),
                                  (45, 85, 150, 75, 90, 90),
                                  (45, 80, 155, 80, 90, 90),
                                  (45, 75, 160, 85, 90, 90),
                                  (45, 70, 165, 90, 90, 90)],
                           "90": [(90, 125, 110, 35, 90, 90),
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
                           "135": [(135, 125, 110, 35, 90, 90),
                                   (135, 120, 115, 40, 90, 90),
                                   (135, 115, 120, 45, 90, 90),
                                   (135, 110, 125, 50, 90, 90),
                                   (135, 105, 130, 55, 90, 90),
                                   (135, 100, 135, 60, 90, 90),
                                   (135, 95, 140, 65, 90, 90),
                                   (135, 90, 145, 70, 90, 90),
                                   (135, 85, 150, 75, 90, 90),
                                   (135, 80, 155, 80, 90, 90),
                                   (135, 75, 160, 85, 90, 90),
                                   (135, 70, 165, 90, 90, 90)],
                           }

    def identify(self):

        counter = 0        
        current_coord = (round(self.kit.servo[2].angle),
                                         round(self.kit.servo[5].angle),
                                         round(self.kit.servo[4].angle),
                                         round(self.kit.servo[1].angle),
                                         round(self.kit.servo[0].angle),
                                         round(self.kit.servo[3].angle))
        for base_list in self.list_coord:
            list_coord = self.dict_coord[str(base_list)]
            if self.y is -1 or self.x is -1:
                for new_coord in list_coord:
                    new_coord = (135, 70, 160, 92, 90, 80)
                    self.move_to_coord(current_coord, new_coord)
                    current_coord = new_coord
                    counter += 1

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
        sleep(0.2)


if __name__ == "__main__":
    unwanted_obj = Robot()
    unwanted_obj.identify()
