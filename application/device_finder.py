from PyQt4 import QtCore
from serial_interface import SerialInterface
import sys

class DeviceFinder(QtCore.QThread):
    
    foundDevice = QtCore.pyqtSignal(str, SerialInterface)

    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.getKnownPorts()
        self.found = []

    def getKnownPorts(self):
        if 'win32' in sys.platform:
            # windows
            self.ports = ["COM0", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "COM10", "COM11", "COM12", "COM13", "COM14", "COM15", "COM16", "COM17", "COM18", "COM19", "COM20", "COM21", "COM22", "COM23", "COM24", "COM25", "COM26", "COM27", "COM28", "COM29", "COM30", "COM31", "COM32", "COM33", "COM34", "COM35", "COM36", "COM37", "COM38", "COM39", "COM40", "COM41", "COM42", "COM43", "COM44", "COM45", "COM46", "COM47", "COM48", "COM49", "COM50"]
        else:
            # linux
            self.ports = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3", "/dev/ttyACM4", "/dev/ttyACM5", "/dev/ttyACM6", "/dev/ttyACM7", "/dev/ttyACM8", "/dev/ttyACM9", "/dev/ttyACM10"]
            self.ports +=  ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2", "/dev/ttyUSB3", "/dev/ttyUSB4", "/dev/ttyUSB5", "/dev/ttyUSB6", "/dev/ttyUSB7", "/dev/ttyUSB8", "/dev/ttyUSB9", "/dev/ttyUSB10"]

    def run(self):
        while True:
            for port in self.ports:
                if port in self.found: continue
                try:
                    serial = SerialInterface(port, 115200)
                    serial.connectToArduino()
                    if serial.isConnected():
                        serial.serial_conn.timeout = 0.2 # read timeout of 200 millisecond
                        samples = serial.getSamples(20)
                        
                        if samples:
                            serial.serial_conn.timeout = None
                            self.foundDevice.emit(port, serial)
                            self.found.append(port)
                        else:
                            serial.disconnect()

                except Exception, e:
                    #print port, e
                    continue
                finally:
                    if serial.isConnected() and not port in self.found:
                        serial.disconnect()

            self.msleep(500)

        self.exec_()


# if __name__ == '__main__':
#     app = QtCore.QCoreApplication(sys.argv)

#     def newDevice(port):
#         print port

#     device_finder = DeviceFinder()
#     device_finder.foundDevice[str].connect(newDevice)
#     device_finder.start()

#     sys.exit(app.exec_())