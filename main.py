import pyaudio
import scipy.fftpack as sf
import numpy as np
import sys
import time
import subprocess

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
CHUNK =2**10

AS_NEXT = b'''
tell application "Keynote"
    activate
    show next
end tell
'''

class SnappingDetector(object):

    def __init__(self):
        self.x = sf.fftfreq(CHUNK, 1.0/RATE)[:int(CHUNK/2)]
        self.audio = pyaudio.PyAudio()
        self.preDetect = -1
        self.lastMeans = [0]
        self.keynote = KeynoteControl()

    def start(self, device):
        self.stream = self.audio.open(
            input=True,
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input_device_index=device,
            frames_per_buffer=CHUNK,
            stream_callback=self.callback)
        print ("Starting detection...")
        self.stream.start_stream()

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
        mean = np.mean(self.y)
        var = np.var(self.y)
        meansMean = np.mean(self.lastMeans)
        freqMean = np.mean(self.x * self.y) / mean

        if self.preDetect == -1:
            if 8000 < freqMean and freqMean < 12000 and 10.0*meansMean < mean and 10000 < mean and 200000000 < var:
                self.preDetect = mean
                self.preDetectTime = time.time()
        elif self.preDetectTime + 0.2 < time.time():
            if mean < self.preDetect:
                print('Patchin!')
                self.keynote.next()
            self.preDetect = -1

        if 10 <= len(self.lastMeans):
            self.lastMeans.pop(0)
        self.lastMeans.append(mean)

        return (None, pyaudio.paContinue)

class KeynoteControl(object):
    def __init__(self):
        return

    def next(self):
        osa = subprocess.Popen('osascript', stdin = subprocess.PIPE)
        osa.stdin.write(AS_NEXT)
        osa.stdin.close()

if __name__ == '__main__':
    a = SnappingDetector()
    for i, device in enumerate(a.getDevices()):
        print(i, device['name'])
    device = input('input device ID > ')
    a.start(int(device))

    inputStr = ""
    while inputStr == "":
        inputStr = input()
