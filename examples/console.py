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
if __name__ == '__main__':
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
    while 1:
        time.sleep(0.25)
        attention_value = 0
        meditation_value = 0
        delta_value = 0
        theta_value = 0
        alpha_value = 0
        beta_value = 0
        gamma_value = 0
        try:
            data = socket.recv(10000)
            parser.feed(data)
        except BluetoothError:
            pass
        if len(recorder.attention)>0:
            attention_value = recorder.attention[-1]
            meditation_value = recorder.meditation[-1]
            flen = 50
            if len(recorder.raw)>=512:
                spectrum, relative_spectrum = bin_power(recorder.raw[-512*3:], range(flen),512)
                spectra.append(array(relative_spectrum))
                if len(spectra)>30:
                    spectra.pop(0)
                spectrum = mean(array(spectra),axis=0)
                for i in range (flen-1):
                    value = float(spectrum[i]*1000)
                    if i<3:
                        delta_value += value
                    elif i<8:
                        theta_value += value
                    elif i<13:
                        alpha_value += value
                    elif i<30:
                        beta_value += value
                    else:
                        gamma_value += value

                print "Attention: {}".format(attention_value)
                print "Meditation {}".format(meditation_value)
                print "Delta: {}".format(delta_value)
                print "Theta: {}".format(theta_value)
                print "Alpha: {}".format(alpha_value)
                print "Beta: {}".format(beta_value)
                print "Gamma: {}".format(gamma_value)
            else:
                pass
