from PyQt4 import QtCore

# a thread with a single signal

class SerialThread(QtCore.QThread):

	# emitted when we got new samples
	gotSamples = QtCore.pyqtSignal(tuple, int)
	deviceDisconnected = QtCore.pyqtSignal()

	def __init__(self, serial_iface, n_samples=1000, parent=None):
		QtCore.QThread.__init__(self, parent)
		self.serial_iface = serial_iface
		self.n_samples = n_samples
		self.stop_ = False

	def stop__(self):
		self.stop_ = True
                
	def run(self):
		while not self.stop_:
			#try:
			samples = self.serial_iface.getSamples(self.n_samples)
			if samples:
				self.gotSamples.emit(samples, self.n_samples)
			#except SerialException, e:
			#	self.deviceDisconnected.emit()

		#self.serial_iface.disconnect()
		self.exec_()
