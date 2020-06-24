import smbus
import math
import time

class Gyro:
    def __init__(self):
        # Register
        self.power_mgmt_1 = 0x6b
        self.power_mgmt_2 = 0x6c
        self.bus = smbus.SMBus(1)  # bus = smbus.SMBus(0) fuer Revision 1
        self.address = 0x68  # via i2cdetect

        # Aktivieren, um das Modul ansprechen zu koennen
        self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)

    def read_byte(self, reg):
        return self.bus.read_byte_data(self.address, reg)

    def read_word(self,reg):
        h = self.bus.read_byte_data(self.address, reg)
        l = self.bus.read_byte_data(self.address, reg + 1)
        value = (h << 8) + l
        return value

    def read_word_2c(self,reg):
        val = self.read_word(reg)
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val

    def dist(self,a, b):
        return math.sqrt((a * a) + (b * b))

    def get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self.dist(y, z))
        return -math.degrees(radians)

    def get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self.dist(x, z))
        return math.degrees(radians)

    def get_x_y(self):
        Acc_xout = self.read_word_2c(0x3b)
        Acc_yout = self.read_word_2c(0x3d)
        Acc_zout = self.read_word_2c(0x3f)

        Acc_xout_scaled = Acc_xout / 16384.0
        Acc_yout_scaled = Acc_yout / 16384.0
        Acc_zout_scaled = Acc_zout / 16384.0

        x_rotation = self.get_x_rotation(Acc_xout_scaled, Acc_yout_scaled, Acc_zout_scaled)
        y_rotation = self.get_y_rotation(Acc_xout_scaled, Acc_yout_scaled, Acc_zout_scaled)
        return x_rotation, y_rotation

if __name__=="__main__":
    g = Gyro()
    while True:
        x,y = g.get_x_y()
        print((x,y))
        time.sleep(2)
