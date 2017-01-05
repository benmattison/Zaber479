from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply, AsciiAxis
import zaberCommands as zc
import time

port = zc.check_serial_ports(portType='AsciiSerial')
devices, numDevices = zc.initialize_zaber_serial(port,maxDevices=10)

num_steps = 300000
num_moves = 2

for i in range(numDevices):
    for j in range(num_moves):
        devices[i].move_rel(num_steps)
        time.sleep(2)
    devices[i].home()
