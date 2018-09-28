#!/usr/bin/python
# -*- coding: utf-8 -*-

from mindwave.parser import ThinkGearParser, TimeSeriesRecorder
import bluetooth
import time
import sys
import argparse
from numpy import *
from scipy import *
from progressbar import ProgressBar, Bar, Percentage
import threading
from mindwave.pyeeg import bin_power
from mindwave.bluetooth_headset import connect_magic, connect_bluetooth_addr
from mindwave.bluetooth_headset import BluetoothError
from example_startup import mindwave_startup

description = """Simple Neurofeedback console application.

Make sure you paired the Mindwave to your computer. You need to
do that pairing for every operating system/user profile you run
seperately.

If you don't know the address, leave it out, and this program will
figure it out, but you need to put the MindWave Mobile headset into
pairing mode first.

"""


class data_miner(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.quite = False
        self.delta = 0
        self.theta = 0
        self.alpha = 0
        self.beta = 0
        self.gamma = 0
        self.data_ready = False

    def run(self):
        extra_args=[dict(name='measure', type=str, nargs='?',
            const="attention", default="attention",
            help="""Measure you want feedback on. Either "meditation"
            or "attention\"""")]
        socket, args = mindwave_startup(description=description,
                              extra_args=extra_args)

        if args.measure not in ["attention", "meditation"]:
            print "Unknown measure %s" % repr(args.measure)
            sys.exit(-1)
        recorder = TimeSeriesRecorder()
        parser = ThinkGearParser(recorders=[recorder])

        spectra = []
        while not self.quite:
            time.sleep(0.05)
            idelta = 0
            itheta = 0
            ialpha = 0
            ibeta = 0
            igamma = 0
            try:
                data = socket.recv(10000)
                parser.feed(data)
            except BluetoothError:
                pass
            if len(recorder.attention)>0:
                flen = 50
                if len(recorder.raw)>=512:
                    self.data_ready = True
                    spectrum, relative_spectrum = bin_power(recorder.raw[-512*3:], range(flen),512)
                    spectra.append(array(relative_spectrum))
                    if len(spectra)>30:
                        spectra.pop(0)
                    spectrum = mean(array(spectra),axis=0)
                    for i in range (flen-1):
                        value = float(spectrum[i]*1000)
                        if i<3:
                            idelta += value
                        elif i<8:
                            itheta += value
                        elif i<13:
                            ialpha += value
                        elif i<30:
                            ibeta += value
                        else:
                            igamma += value
                    if False:
                        print "Delta: {}".format(self.delta)
                        print "Theta: {}".format(self.theta)
                        print "Alpha: {}".format(self.alpha)
                        print "Beta: {}".format(self.beta)
                        print "Gamma: {}".format(self.gamma)
                    self.delta = idelta
                    self.theta = itheta
                    self.alpha = ialpha
                    self.beta = ibeta
                    self.gamma = igamma

    def close(self):
        self.quite = True

if __name__ == '__main__':
    data_miner(printer=True)
