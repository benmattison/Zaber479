from zaber.serial import AsciiSerial, AsciiDevice, AsciiCommand, AsciiReply, AsciiAxis
import zaberCommands as zc


port = zc.check_serial_ports(portType='AsciiSerial')
devices, numDevices = zc.initialize_zaber_serial(port,maxDevices=10)
