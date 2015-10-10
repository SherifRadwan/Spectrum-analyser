import serial
import time

class SerialInterface(object):

	def __init__(self, port='', baud=9600):
		self.port = port
		self.baud = baud
		self.serial_conn = None
		
	def connectToArduino(self):
		port = self.port
		baud = self.baud

		try:
			self.serial_conn = serial.Serial()
			self.serial_conn.port = port
			self.serial_conn.baudrate = baud
			self.serial_conn.open()
			self.flush()
		except serial.SerialException, e:
			self.serial_conn = None
			#raise e
			#print "can not connect to serial port at %s\n%s" % (port, str(e))

	def isConnected(self):
		return self.serial_conn is not None

	def getSamples(self, n):
		t = None
		s = []
		c = 0
		if self.isConnected():
			start = time.time()
			
			while self.serial_conn.inWaiting >= 3:
				if(ord(self.serial_conn.read()) == 0x00):
					# get sample
					low, high =  self.serial_conn.read(2) #low, high byte
					sample = ord(low) + (ord(high) << 8)
					#sample = self.serial_conn.readline().rstrip()
				
					try:
						s.append(int(sample))
					except:
						continue

					c += 1
					if c == n:
						break

			end = time.time()
			T = end - start # sampling time
			return (T, s)

		return None

	def flush(self):
		self.serial_conn.flush()

	def disconnect(self):
		if self.isConnected():
			self.serial_conn.close()

if __name__ == '__main__':
	iface = SerialInterface('/dev/ttyUSB0', 115200)
	iface.connectToArduino()

	if iface.isConnected():
		print iface.serial_conn.readline()
		print iface.serial_conn.readline()

		while True:
			samples =  iface.getSamples(1000)
			if samples:
				print samples[0]
				print samples[1]

	print "disconnecting..."
	iface.disconnect()
