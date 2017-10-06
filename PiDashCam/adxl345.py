import math
import time
import smbus

import i2cutils as I2CUtils

class ADXL345(object):
    '''
    Simple ADXL345 implementation
    Datasheet: http://www.analog.com/en/mems-sensors/mems-inertial-sensors/adxl345/products/product.html
    '''

    POWER_CTL = 0x2d
    DATA_FORMAT = 0x31
    FIFO_CTL = 0x38
    
    AFS_2g = 0
    AFS_4g = 1
    AFS_8g = 2
    AFS_16g = 3

    ACCEL_START_BLOCK = 0x32
    ACCEL_XOUT_H = 1
    ACCEL_XOUT_L = 0
    ACCEL_YOUT_H = 3
    ACCEL_YOUT_L = 2
    ACCEL_ZOUT_H = 5
    ACCEL_ZOUT_L = 4

    ACCEL_SCALE = 0.004 # Always set to this as we are using FULL_RES

    def __init__(self, bus, address, name, afs_scale=AFS_2g):
        '''
        Constructor
        '''

        self.bus = bus
        self.address = address
        self.name = name

        self.afs_scale = afs_scale
        
        self.raw_accel_data = [0, 0, 0, 0, 0, 0]
        
        self.accel_raw_x = 0
        self.accel_raw_y = 0
        self.accel_raw_z = 0
        
        self.accel_scaled_x = 0
        self.accel_scaled_y = 0
        self.accel_scaled_z = 0
        
        self.pitch = 0.0
        self.roll = 0.0
        self.last_time = time.time()
        self.time_diff = 0
        
        
        # Wake up the device
        I2CUtils.i2c_write_byte(self.bus, self.address,ADXL345.POWER_CTL, 0b00001000)
        
        # Set data to FULL_RES and user defined scale 
        data_format = 1 << 3 | afs_scale
        I2CUtils.i2c_write_byte(self.bus, self.address,ADXL345.DATA_FORMAT, data_format)

        # Disable FIFO mode
        I2CUtils.i2c_write_byte(self.bus, self.address,ADXL345.FIFO_CTL, 0b00000000)
           
    def read_raw_data(self):
        self.raw_accel_data = I2CUtils.i2c_read_block(self.bus, self.address, ADXL345.ACCEL_START_BLOCK, 6)
        
        self.accel_raw_x = I2CUtils.twos_compliment(self.raw_accel_data[ADXL345.ACCEL_XOUT_H], self.raw_accel_data[ADXL345.ACCEL_XOUT_L])
        self.accel_raw_y = I2CUtils.twos_compliment(self.raw_accel_data[ADXL345.ACCEL_YOUT_H], self.raw_accel_data[ADXL345.ACCEL_YOUT_L])
        self.accel_raw_z = I2CUtils.twos_compliment(self.raw_accel_data[ADXL345.ACCEL_ZOUT_H], self.raw_accel_data[ADXL345.ACCEL_ZOUT_L])

        self.accel_scaled_x = self.accel_raw_x * ADXL345.ACCEL_SCALE
        self.accel_scaled_y = self.accel_raw_y * ADXL345.ACCEL_SCALE
        self.accel_scaled_z = self.accel_raw_z * ADXL345.ACCEL_SCALE
        
    def distance(self, x, y):
        '''Returns the distance between two point in 2d space'''
        return math.sqrt((x * x) + (y * y))
    
    def read_x_rotation(self, x, y, z):
        '''Returns the rotation around the X axis in radians'''
        return (math.atan2(y, self.distance(x, z)))
    
    def read_y_rotation(self, x, y, z):
        '''Returns the rotation around the Y axis in radians'''
        return (-math.atan2(x, self.distance(y, z)))
    
    def read_raw_accel_x(self):
        '''Return the RAW X accelerometer value'''
        return self.accel_raw_x
        
    def read_raw_accel_y(self):
        '''Return the RAW Y accelerometer value'''
        return self.accel_raw_y
        
    def read_raw_accel_z(self):
        '''Return the RAW Z accelerometer value'''        
        return self.accel_raw_z
    
    def read_scaled_accel_x(self):
        '''Return the SCALED X accelerometer value'''
        return self.accel_scaled_x
    
    def read_scaled_accel_y(self):
        '''Return the SCALED Y accelerometer value'''
        return self.accel_scaled_y

    def read_scaled_accel_z(self):
        '''Return the SCALED Z accelerometer value'''
        return self.accel_scaled_z

    
    def read_pitch(self):
        '''Calculate the current pitch value in radians'''
        x = self.read_scaled_accel_x()
        y = self.read_scaled_accel_y()
        z = self.read_scaled_accel_z()
        return self.read_x_rotation(x, y, z)

    def read_roll(self):
        '''Calculate the current roll value in radians'''
        x = self.read_scaled_accel_x()
        y = self.read_scaled_accel_y()
        z = self.read_scaled_accel_z()
        return self.read_y_rotation(x, y, z)

if __name__ == "__main__":
    bus = smbus.SMBus(I2CUtils.i2c_raspberry_pi_bus_number())
    adxl345=ADXL345(bus, 0x53, "accel")
    adxl345.read_raw_data()
    print adxl345.read_scaled_accel_x()
    print adxl345.read_scaled_accel_y()
    print adxl345.read_scaled_accel_z()
