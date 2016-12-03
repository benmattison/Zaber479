import zaberCommands as zc

ser,port = zc.check_serial_ports()
devices, numDevices = zc.initialize_zaber_serial(port,maxDevices=10)