#!/usr/bin/python

def i2c_raspberry_pi_bus_number():
    """Returns Raspberry Pi I2C bus number (integer, 0 or 1).

    Looks at `/proc/cpuinfo` to identify if this is a revised model
    of the Raspberry Pi (with 512MB of RAM) using `/dev/i2c-1`, or
    the original version (with 256MB or RAM) using `/dev/i2c-0`.
    """
    cpuinfo = 1
    with open('/proc/cpuinfo','r') as f:
        for line in f:
            if line.startswith('Revision'):
                cpuinfo = line.strip()[-1:]
    return (1 if (cpuinfo >'3') else 0)
    
def i2c_read_byte(bus, address, register):
    return bus.read_byte_data(address, register)
 
def i2c_read_word_unsigned(bus, address, register):
    high = bus.read_byte_data(address, register)
    low = bus.read_byte_data(address, register+1)
    return (high << 8) + low

def i2c_read_word_signed(bus, address, register):
    value = i2c_read_word_unsigned(bus, address, register)
    if (value >= 0x8000):
        return -((0xffff - value) + 1)
    else:
        return value

def i2c_write_byte(bus, address, register, value):
    bus.write_byte_data(address, register, value)

def i2c_read_block(bus, address, start, length):
    return bus.read_i2c_block_data(address, start, length)

def twos_compliment(high_byte, low_byte):
    value = (high_byte << 8) + low_byte
    if (value >= 0x8000):
        return -((0xffff - value) + 1)
    else:
        return value
        
if __name__ == "__main__":
    print i2c_raspberry_pi_bus_number()