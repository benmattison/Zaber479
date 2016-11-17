# Full manual for ASCII Protocol to Zaber Stages: http://www.zaber.com/wiki/Manuals/ASCII_Protocol_Manual
# Python API: http://www.zaber.com/support/docs/api/core-python/0.8.1/

import serial
import time
import sys
import glob
from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply, AsciiAxis


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


def check_serial_ports():
    """
    :return ser: Serial reference to correct COM port
    :return port: Zaber AsciiSerial reference to correct COM port
    """

    # Find serial ports on the system
    COMports = serial_ports()
    print(len(COMports))

    # Connect to the serial port with the Zaber stage (if more than one on system).
    if len(COMports) > 1:
        print('Multiple COM ports found, please identify which is connected to Zaber stage')
        c = raw_input('Enter COM port number followed by ENTER: ')
        ser = serial.Serial('COM%d'%c,115200,timeout=1)
        port = AsciiSerial('COM%d'%c)
    else:
        ser = serial.Serial(COMports[0],115200,timeout=1)
        port = AsciiSerial(COMports[0])

    return ser, port


def initialize_zaber_serial(port, **kwargs):
    """
    :param port: AsciiSerial COM port reference for stages
    :param kwargs: can specify maximum number of devices to check for (maxDevices=X). Default is 10
    :return devices: list of AsciiDevices corresponding to all Zaber stages
    :return numDevices: number of devices that were found and initialized
    """
    maxDevices = 10
    for key in kwargs:
        if key == 'maxDevices':
            maxDevices = kwargs[key]

    #print(maxDevices)

    devices = {}
    numDevices = maxDevices
    for i in range (0,maxDevices):
        try:
            devices[i] = AsciiDevice(port, i)# Device number i
            devices[i].home()
        except:
            numDevices = i
            break

    print('Number of initialized devices is: ' + str(numDevices))

    return devices, numDevices


def check_command_succeeded(reply):
    """
    Return true if command succeeded, print reason and return false if command
    rejected

    param reply: AsciiReply

    return: boolean
    """
    if reply.reply_flag != "OK": # If command not accepted (received "RJ")
        print ("Danger! Command rejected because: {}".format(reply.data))
        return False
    else: # Command was accepted
        return True


if __name__ == '__main__':

    ser,port = check_serial_ports()

    # 1) USE SERIAL TO TALK TO STAGES DIRECTLY

    # Example set of commands to follow.
    msgs = ['/1 move abs 30000\n','/1 move rel -20000\n','/1 home\n']

    line = send_rec('/2 \n')
    print(line)
    if line == '':
        print('no stage at address 2')
    #line = send_rec('/1 \n')
    #print(line)

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

    # Close the connection.
    ser.close()

    # 2) USE ZABERSERIAL TO TALK TO STAGES

    devices,numDevices = initialize_zaber_serial(port,numDevices=10)

    # Move stages, check status
    reply = {}
    for i in range (0,numDevices-1):
        devices[i].move_rel(20000) # move devices 20000 microsteps relative to their current positions
        reply[i] = devices[i].send('get pos')
        if check_command_succeeded(reply[i]):
            print("Device %d is at: " %i + reply[i].data)
        else:
            print("Device move failed.")

    # Close the connection
    port.close()