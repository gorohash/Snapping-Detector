import pyaudio
import scipy.fftpack as sf
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import sys

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK =2**10

class AudioFFT(object):

    def __init__(self):
        self.x = sf.fftfreq(CHUNK, 1.0/RATE)[:int(CHUNK/2)]
        self.audio = pyaudio.PyAudio()

    def start(self, device):
        self.stream = self.audio.open(
            input=True,
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input_device_index=device,
            frames_per_buffer=CHUNK,
            stream_callback=self.callback)

        print ("recording...")
        self.stream.start_stream()
        self.g = Graph()
        self.g.setButton(self)

    def getDevices(self):
        count = self.audio.get_device_count()
        devices = []
        for i in range(self.audio.get_device_count()):
            devices.append(self.audio.get_device_info_by_index(i))
        return devices

    def update(self):
        self.g.curve.setData(self.x, self.y)

    def callback(self, in_data, frame_count, time_info, status):
        result = sf.fft(np.fromstring(in_data, dtype=np.int16))
        self.y = np.abs(result)[:int(CHUNK/2)]
        if 10000 < np.mean(self.y) and 100000000 < np.var(self.y):
            print(np.mean(self.y), np.var(self.y))
        return (None, pyaudio.paContinue)

class Graph(object):

    def __init__(self):
        self.win=pg.GraphicsWindow()
        self.win.setWindowTitle("My Graph")
        self.plt=self.win.addPlot()
        self.plt.setYRange(0,100000)
        self.plt.setXRange(0,24000)
        self.curve=self.plt.plot()

    def close(self, audio):
        print("Quitting...")
        self.audio.stream.stop_stream()
        self.audio.stream.close()
        self.audio.audio.terminate()
        QtGui.QApplication.closeAllWindows()

    def setButton(self, audio):
        self.audio = audio
        self.button = QtGui.QPushButton('Close', self.win)
        self.button.move(self.win.width()/2.5, 0)
        self.button.clicked.connect(self.close)
        self.button.show()


if __name__ == '__main__':

    a = AudioFFT()
    for i, device in enumerate(a.getDevices()):
        print(i, device['name'])
    device = input('input device ID >')
    a.start(int(device))

    timer = QtCore.QTimer()
    timer.timeout.connect(a.update)
    timer.start(10)
    if (sys.flags.interactive!=1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
