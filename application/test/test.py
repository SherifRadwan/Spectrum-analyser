from PyQt4 import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
from math import sin, pi

# from stackoverflow
def drange(start, stop, step):
	r = start
	while r < stop:
		yield r
		r += step

def drange(start, stop, step):
	r = start
	while r < stop:
		yield r
		r += step

def approx_value_of(value, n):
	return round(value * n) / n

def func(t, f):
	return 2 * sin(2 * pi * f * t) + 2

class Window(pg.GraphicsWindow):

	def __init__(self, parent=None):
		pg.GraphicsWindow.__init__(self, title="Spectrum Analyzer")
		self.resize(400,300)
		self.setWindowTitle('Spectrum Analyzer')
		pg.setConfigOptions(antialias=True)
		self.plot_item = self.addPlot(title='Time Domain - u(t)', labels={'left': 'u(t)', 'bottom': 't'})
		self.plot_samples()

	def plot_samples(self):
		step = 0.001 #delay
		t = [v for v in drange(0, 0.5, step)]
		u = [approx_value_of(func(i, 40), 100) for i in t]

		self.plot_item.plot(x=t, y=u)

if __name__ == '__main__':
	import sys
	app = QtGui.QApplication(sys.argv)

	win = Window()
	win.show()

	sys.exit(app.exec_())
