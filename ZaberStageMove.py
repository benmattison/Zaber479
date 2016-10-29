from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply, AsciiAxis, BinarySerial, BinaryDevice, BinaryCommand, BinaryReply
import time

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



# Open a serial port. You may need to edit this section for your particular
# hardware and OS setup.
port = AsciiSerial("COM3")         # Windows

# Get a handle for device #1 on the serial chain. This assumes you have a
# device already in ASCII 115,220 baud mode at address 1 on your port.
device = AsciiDevice(port, 1)# Device number 1
device2 = AsciiDevice(port, 2)# Device number 2
device3 = AsciiDevice(port,3)# Device number 3

#Initializing the devices as axis uneccessary  for devices with only one axis, for demonstration.
axis1 = device.axis(1)
axis2 = device2.axis(1)
axis3 = device3.axis(1)


reply1 = axis1.home() # Home the fist axis and check the result.
axis2.move_rel(200000) # move device 2 200000 microsteps relative to its current pos
axis3.move_rel(200000) # move device 3 200000 microsteps relative to its current pos

#get position of device 2 and 3
reply2 = axis2.send('get pos')
reply3 = axis2.send('get pos')

#check if Home command exicuted
if check_command_succeeded(reply1):
    print("Axis 1 Homed.")
    print('Axis 2 position is now' + reply2.data)
    print('Axis 3 position is now' + reply3.data)
else:
    print("Device home failed.")
    exit(1)



# Make the device has finished its previous move before sending the
# next command. Note that this is unnecessary in this case as the
# AsciiDevice.home command is blocking, but this would be required if
# the AsciiDevice.send command is used to trigger movement.
axis3.poll_until_idle()

axis3.home()
axis2.home()

#Now move the device to a non-home position.
#Device also works the same as axis for devices with only one axis
reply1 = device.move_abs(200000) # move to absolute position of 200000 microsteps relative to home
if not check_command_succeeded(reply1):
    print("Device move failed.")
    exit(1)

#Wait for the move to finish.
device.poll_until_idle()

#Read back what position the device thinks it's at.
reply = device.send("get pos")
print("Device position is now " + reply.data)

# Clean up.
port.close()