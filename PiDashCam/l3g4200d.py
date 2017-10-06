import math

import i2cutils as I2CUtils

class L3G4200D(object):
    '''
    Simple L3G4200D implementation
    Datasheet: http://www.st.com/web/catalog/sense_power/FM89/SC1288/PF250373
    '''

    CTRL_REG1 = 0x20
    CTRL_REG2 = 0x21
    CTRL_REG3 = 0x22
    CTRL_REG4 = 0x23
    CTRL_REG5 = 0x24

    GYRO_START_BLOCK = 0x28
    GYRO_XOUT_H = 0x28
    GYRO_XOUT_L = 0x29
    GYRO_YOUT_H = 0x2a
    GYRO_YOUT_L = 0x2b
    GYRO_ZOUT_H = 0x2c
    GYRO_ZOUT_L = 0x2d

    FS_250 = 250
    FS_500 = 500
    FS_2000 = 2000

    FS_250_SCALE = 8.75 / 1000  # milli degrees per second page 10 of the datasheet
    FS_500_SCALE = 17.50 / 1000  # milli degrees per second page 10 of the datasheet
    FS_2000_SCALE = 70.00 / 1000  # milli degrees per second page 10 of the datasheet


    GYRO_SCALE = { FS_250 : [FS_250_SCALE, 0], FS_500 : [FS_500_SCALE, 1], FS_2000 : [FS_2000_SCALE, 10] }

    def __init__(self, bus, address, name, fs_scale=FS_250):
        '''
        Constructor
        '''

        self.bus = bus
        self.address = address
        self.name = name
        self.fs_scale = fs_scale
        
        self.gyro_raw_x = 0
        self.gyro_raw_y = 0
        self.gyro_raw_z = 0
        
        self.gyro_scaled_x = 0
        self.gyro_scaled_y = 0
        self.gyro_scaled_z = 0
        
        self.raw_temp = 0
        self.scaled_temp = 0
        
        # Wake up the deice and get output for each of the three axes,X, Y & Z
        I2CUtils.i2c_write_byte(self.bus, self.address, L3G4200D.CTRL_REG1, 0b00001111)
        
        # Select Big endian so we can use existing I2C library and include the scaling
        ctrl_reg4 = 1 << 6 | L3G4200D.GYRO_SCALE[fs_scale][1] << 4
        I2CUtils.i2c_write_byte(self.bus, self.address, L3G4200D.CTRL_REG4, ctrl_reg4)

    def read_raw_data(self):
        
        self.gyro_raw_x = I2CUtils.i2c_read_word_signed(self.bus, self.address, L3G4200D.GYRO_XOUT_H)
        self.gyro_raw_y = I2CUtils.i2c_read_word_signed(self.bus, self.address, L3G4200D.GYRO_YOUT_H)
        self.gyro_raw_z = I2CUtils.i2c_read_word_signed(self.bus, self.address, L3G4200D.GYRO_ZOUT_H)

        # We convert these to radians for consistency and so we can easily combine later in the filter
        self.gyro_scaled_x = math.radians(self.gyro_raw_x * L3G4200D.GYRO_SCALE[self.fs_scale][0]) 
        self.gyro_scaled_y = math.radians(self.gyro_raw_y * L3G4200D.GYRO_SCALE[self.fs_scale][0]) 
        self.gyro_scaled_z = math.radians(self.gyro_raw_z * L3G4200D.GYRO_SCALE[self.fs_scale][0]) 

    def read_raw_gyro_x(self):
        '''Return the RAW X gyro value'''
        return self.gyro_raw_x
        
    def read_raw_gyro_y(self):
        '''Return the RAW Y gyro value'''
        return self.gyro_raw_y
        
    def read_raw_gyro_z(self):
        '''Return the RAW Z gyro value'''
        return self.gyro_raw_z
    
    def read_scaled_gyro_x(self):
        '''Return the SCALED X gyro value in radians/second'''
        return self.gyro_scaled_x

    def read_scaled_gyro_y(self):
        '''Return the SCALED Y gyro value in radians/second'''
        return self.gyro_scaled_y

    def read_scaled_gyro_z(self):
        '''Return the SCALED Z gyro value in radians/second'''
        return self.gyro_scaled_z
