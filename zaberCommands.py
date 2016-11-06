# http://www.zaber.com/wiki/Manuals/ASCII_Protocol_Manual
# Full manual for ASCII Protocol to Zaber Stages

import serial
import time
import sys
import glob

def send_rec(msg):
    ser.write(msg)
    line = ser.readline()
    print(line)
    return line

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

# Print the names of serial ports available.
if __name__ == '__main__':
    print(serial_ports())

# Find the serial ports available on the system. Hopefully there is only 1.
COMports = serial_ports()

# Connect to the serial port with the Zaber stage.
ser = serial.Serial(COMports[0],115200,timeout = 1)

# Example set of commands to follow.
msgs = ['/1 move rel 20000\n','/1 move abs 300000\n','/1 home\n']

# Send them all and see if they are ready.
for msg in msgs:
    line = send_rec(msg)
    # Assume that the stage is doing something.
    busy = 1
    while busy:
        # Send a command that just asks for the status of device 1.
        line = send_rec('/1 \n')
        # If it is not doing anything, we can send a new command.
        if 'IDLE' in line:
            # busy = 0
            break
        time.sleep(0.5)

# Check if there are any unread lines
line = ser.readlines()
print(line)

# close the connection.
ser.close()