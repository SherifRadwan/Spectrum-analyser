from PyQt4 import QtCore, QtGui, uic
import sys
import pyqtgraph as pg

from serial_interface import SerialInterface
from serial_thread import SerialThread
from device_finder import DeviceFinder

import numpy as np
import math


# from stackoverflow
# FIXME: use numpy or scipy functions instead!!
# linespace ?? float support
def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step

# from PlotItem.py
# returns the power spectrum of y(x)
# original one
# def _fourierTransform(self, x, y):
#     ## Perform fourier transform. If x values are not sampled uniformly,
#     ## then use np.interp to resample before taking fft.
#     dx = np.diff(x)
#     uniform = not np.any(np.abs(dx-dx[0]) > (abs(dx[0]) / 1000.))
#     if not uniform:
#         x2 = np.linspace(x[0], x[-1], len(x))
#         y = np.interp(x2, x, y)
#         x = x2
#     f = np.fft.fft(y) / len(y)
#     y = abs(f[1:len(f)/2])
#     dt = x[-1] - x[0]
#     x = np.linspace(0, 0.5*len(x)/dt, len(y))
#     return x, y

def _fourierTransform(x, y):
    ## Perform fourier transform. If x values are not sampled uniformly,
    ## then use np.interp to resample before taking fft.
    dx = np.diff(x)
    uniform = not np.any(np.abs(dx-dx[0]) > (abs(dx[0]) / 1000.))
    if not uniform:
        x2 = np.linspace(x[0], x[-1], len(x))
        y = np.interp(x2, x, y)
        x = x2
    f = np.fft.fft(y) / len(y)
    h_f = f[1:len(f)/2]
    y = abs(h_f)
    dt = x[-1] - x[0]
    x = np.linspace(0, 0.5*len(x)/dt, len(y))
    return x, h_f 

def powerSpectrum(ft):
    x, y = ft
    return x, abs(y)

def amplitudeSpectrum(ft):
    x, y = ft
    return x, 20*np.log10(np.absolute(y))

def phaseSpectrum(ft):
    x, y = ft
    return x, np.angle(y)

class MainWindow(QtGui.QMainWindow):

	def __init__(self):
		QtGui.QMainWindow.__init__(self, None)
		uic.loadUi('mainwindow.ui', self)
		self.resize(700, 500)

		self.plotWindow = PlotWindow()
		self.stackedPlots.addWidget(self.plotWindow)
		self.stackedPlots.setCurrentIndex(0)

		self.actionRefresh.triggered[bool].connect(self.refreshList)
		self.actionConnect.triggered[bool].connect(self.connectFromList)
		self.actionDisconnect.triggered[bool].connect(self.disconnectFromCurrentDevice)
		self.actionLock.toggled[bool].connect(self.hold)
		self.actionViewAll.toggled[bool].connect(self.autoSet)
		self.actionExport.triggered[bool].connect(self.exportData)
		self.actionQuit.triggered[bool].connect(self.quitApp)
		self.actionAbout.triggered[bool].connect(self.aboutApp)

		self.listDevices.itemSelectionChanged.connect(self.deviceListChanged)

		self.actionViewAll.setChecked(True)
		self.autoSet(self.actionViewAll.isChecked())

		self.ifaces = []
		self.port = None
		self.baud = 115200
		self.iface = None
		self.iface_thread = None

		self.initDeviceFinder()
		self.disableControls()

		self.deviceListChanged()


		self.statusBar().showMessage('Ready.')
		
	def deviceListChanged(self):
		if self.listDevices.count() > 0:
			self.actionConnect.setEnabled(True)
			self.enableControls()
		else:
			self.actionConnect.setEnabled(False)
			self.disableControls()

	def disableControls(self):
		self.plotWindow.setEnabled(False)
		self.actionDisconnect.setEnabled(False)
		self.actionLock.setEnabled(False)
		self.actionViewAll.setEnabled(False)
		self.actionExport.setEnabled(False)

	def enableControls(self):
		self.plotWindow.setEnabled(True)
		self.actionDisconnect.setEnabled(True)
		self.actionLock.setEnabled(True)
		self.actionViewAll.setEnabled(True)
		self.actionExport.setEnabled(True)

	def initDeviceFinder(self):
		self.device_finder = DeviceFinder()
		self.device_finder.foundDevice[str, SerialInterface].connect(self.gotNewDevice)
		self.device_finder.start()

	def gotNewDevice(self, port, iface):
		self.port = port
		self.listDevices.addItem(QtGui.QListWidgetItem(QtGui.QIcon('icons/device.png'), port))
		self.ifaces.append(iface)

		self.statusBar().showMessage('Found %d device(s).' % self.listDevices.count())

	def startSampling(self):
		self.iface_thread.start()

	def stopSampling(self):
		self.iface_thread.stop__()
		self.iface_thread.exit()

	def connectDevice(self):
		if not self.iface:
			self.iface = self.ifaces[self.listDevices.currentRow()]

		if self.iface:
			if not self.iface.isConnected():
				self.iface = SerialInterface(self.port, self.baud)
				self.iface.connectToArduino()

			if not self.iface.serial_conn.isOpen():
				self.iface.serial_conn.open()
				
			if self.iface.isConnected():
				if self.iface_thread:
					del self.iface_thread
			
				self.iface_thread = SerialThread(self.iface)
				self.iface_thread.n_samples = 1000
				self.iface_thread.gotSamples[tuple, int].connect(self.plotWindow.plotSamples)
				#self.iface_thread.deviceDisconnected.connect(self.disconnectFromCurrentDevice)

				self.startSampling()

				return True

		return False

	def refreshList(self):
		self.statusBar().showMessage('Searching...')

		for i in range(0, self.listDevices.count()):
			port = self.listDevices.item(i).text()
			self.device_finder.found.remove(port)

		self.listDevices.clear()
		self.ifaces = []

	def connectFromList(self):
		self.actionConnect.setEnabled(False)
		self.actionDisconnect.setEnabled(True)
		self.actionRefresh.setEnabled(False)

		#self.connectDevice(self.listDevices.currentItem().text())
		if self.connectDevice():
			self.enableControls()
		else:
			QtGui.QMessageBox.critical(self, 'Error', 'Cannot connect to the device, refresh the list')

	def disconnectFromCurrentDevice(self):
		self.actionConnect.setEnabled(True)
		self.actionDisconnect.setEnabled(False)
		self.actionRefresh.setEnabled(True)
		self.disableControls()

		try:
			self.stopSampling()
			self.iface.disconnect()
		except:
			pass

		self.iface = None
		self.plotWindow.plot_item_a.clear()
		self.plotWindow.plot_item_p.clear()

	def exportData(self):
		self.plotWindow.scene().showExportDialog()

	def hold(self, checked):
		if checked:
			self.stopSampling()
		else:
			self.connectDevice()
			self.startSampling()

	def autoSet(self, checked):
		if checked:
			self.plotWindow.plot_item_a.enableAutoRange()
			self.plotWindow.plot_item_p.enableAutoRange()
		else:
			self.plotWindow.plot_item_a.disableAutoRange()
			self.plotWindow.plot_item_p.disableAutoRange()


	def quitApp(self):
		try:
			self.disconnectFromCurrentDevice()
		except:
			pass

		QtGui.QApplication.exit(0)

	def aboutApp(self):
		QtGui.QMessageBox.about(self, 'About',
							    """<b>Spectrum Analyzer</b><br>Computer Peripherals Interface Project<br><b>By:</b><br>Sherif Adel Radwan<br>Mahmoud Sayed Zainhom<br>Abdelrahman Ghanem Abdelrady""")
	
	def closeEvent(self, event):
		if self.iface:
			self.iface.disconnect()

class PlotWindow(pg.GraphicsWindow):

	def __init__(self, parent=None):
		pg.GraphicsWindow.__init__(self, title="Amplitude Spectrum")
		pg.setConfigOption('background', '')
		pg.setConfigOptions(antialias=True)
		self.plot_item_a = self.addPlot(title='Amplitude Spectrum', labels={'left': 'Amplitude', 'bottom': 'Freq (f)'})
		self.plot_item_p = self.addPlot(title='Phase Spectrum', labels={'left': 'Phase', 'bottom': 'Freq (f)'})
		
		self.plot_item_a.disableAutoRange()
		self.plot_item_p.disableAutoRange()
		self.plot_item_a.showGrid(x=True, y=True)
		self.plot_item_p.showGrid(x=True, y=True)

	def approxValueOf(self, value, n):
		return round(value * n) / n

	def plotSamples(self, samples, n):
		T = samples[0]
		s = samples[1]

		t = [x for x in drange(0, T, T/n)][:n]
		#u = [self.approx_value_of(v/1023.0 * 5, 10) for v in s]
		#u = [(v/1023.0 * 5) for v in s]
		# accoring to the voltage divider of the circuit
		u = [11 * (v/1023.0 * 5) - 25 for v in s]

		#FFT = scipy.fft(u)
		#ampl = 20*scipy.log10(abs(FFT))
		#phase = 
		#freqs = scipy.fftpack.fftfreq(len(u), t[1]-t[0])

		# fft = np.fft.fft(u) / len(u)
		# single_sidded_fft = abs(fft[1:len(fft)/2])
		# freqs = [f for f in drange(0, len(single_sidded_fft), 0.5*T/n)]

		pen = pg.mkPen('g', width=2)

		single_side_fft = _fourierTransform(t, u)
		f_amp, amp_spect = amplitudeSpectrum(single_side_fft)
		f_phs, phs_spect = phaseSpectrum(single_side_fft)

		self.plot_item_a.plot(x=f_amp, y=amp_spect, clear=True, pen=pen)
		self.plot_item_p.plot(x=f_phs, y=phs_spect, clear=True, pen=pen)

if __name__ == '__main__':
	app = QtGui.QApplication(sys.argv)

	win = MainWindow()
	win.show()

	sys.exit(app.exec_())
