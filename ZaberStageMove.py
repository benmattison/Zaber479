from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply, AsciiAxis
import time
import sys
import glob
import serial


#This is an example on how to initiate the  motion devices and give them commands

# Helper to check that commands succeeded.
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


if __name__ == '__main__':

    # Open a serial port. You may need to edit this section for your particular
    # hardware and OS setup.
    port = AsciiSerial("COM3")

    # Get a handle for device #1 on the serial chain. This assumes you have a
    # device already in ASCII 115,220 baud mode at address 1 on your port.
    # Finds how many devices there are and homes them all
    maxDevices = 10
    numDevices = maxDevices
    device = {}
    for i in range (0,maxDevices):
        try:
            device[i] = AsciiDevice(port, i)# Device number i
            device[i].home()
        except:
            break

    numDevices = i
    print(numDevices)

    #Initializing the devices as axis uneccessary for devices with only one axis, for demonstration.]
    axis = {}
    for i in range (0,numDevices-1):
        axis[i] = device[i].axis(1)

    reply = {}
    for i in range (0,numDevices-1):
        reply[i] = axis[i].home() # Home the fist axis and check the result.

    print(reply)

    # Move stages
    for i in range (0,numDevices-1):
        axis[i].move_rel(20000) # move devices 20000 microsteps relative to their current positions

    # Get position of stages and check if move commands executed
    for i in range (0,numDevices - 1):
        reply[i] = axis[i].send('get pos')
        if check_command_succeeded(reply[i]):
            print("Device %d is at: " %i + reply[i].data)
        else:
            print("Device move failed.")
            exit(1)

    print(reply)


    # # Make the device has finished its previous move before sending the
    # # next command. Note that this is unnecessary in this case as the
    # # AsciiDevice.home command is blocking, but this would be required if
    # # the AsciiDevice.send command is used to trigger movement.
    # axis3.poll_until_idle()
    #
    # axis3.home()
    # axis2.home()
    #
    # #Now move the device to a non-home position.
    # #Device also works the same as axis for devices with only one axis
    # reply1 = d['device1'].move_abs(200000) # move to absolute position of 200000 microsteps relative to home
    # if not check_command_succeeded(reply1):
    #     print("Device move failed.")
    #     exit(1)
    #
    # #Wait for the move to finish.
    # d['device1'].poll_until_idle()
    #
    # #Read back what position the device thinks it's at.
    # reply = d['device1'].send("get pos")
    # print("Device position is now " + reply.data)

    # Clean up.
    port.close()