import threading
import os
from numpy import *
from time import sleep

import console


class calibrator(object):

    def __init__(self):
        self.miner = console.data_miner()
        self.miner.start()
        self.updater = threading.Thread(target=self.updater).start()
        self.quite = False
        self.recording = False
        self.added_values = False
        self.output = open(os.path.join(os.curdir, "calib.conf"), "w")
        self.length = 50
        self.delta_q = []
        self.delta_std = 0
        self.delta_avg = 0
        self.theta_q = []
        self.theta_std = 0
        self.theta_avg = 0
        self.alpha_q = []
        self.alpha_std = 0
        self.alpha_avg = 0
        self.beta_q = []
        self.beta_std = 0
        self.beta_avg = 0
        self.gamma_q = []
        self.gamma_std = 0
        self.gamma_avg = 0

    def update_values(self):
        while self.miner.delta == 0:
            sleep(.01)
        self.delta_q.append(self.miner.delta)
        self.theta_q.append(self.miner.theta)
        self.alpha_q.append(self.miner.alpha)
        self.beta_q.append(self.miner.beta)
        self.gamma_q.append(self.miner.gamma)
        if len(self.delta_q) > self.length:
            self.delta_q.pop(0)
            self.theta_q.pop(0)
            self.alpha_q.pop(0)
            self.beta_q.pop(0)
            self.gamma_q.pop(0)
        if not self.added_values:
            print "ready!"
            self.added_values = True

    def print_recent_values(self):
        print "Delta: {}, Std Dev: {}".format(self.delta_q[-1], self.delta_std)
        print "Theta: {}, Std Dev: {}".format(self.theta_q[-1], self.theta_std)
        print "Alpha: {}, Std Dev: {}".format(self.alpha_q[-1], self.alpha_std)
        print "Beta: {}, Std Dev: {}".format(self.beta_q[-1], self.beta_std)
        print "Gamma: {}, Std Dev: {}".format(self.gamma_q[-1], self.gamma_std)
            
    def calculate_std_dev(self):
        self.delta_std = std(self.delta_q)
        self.detla_avg = average(self.delta_q)
        self.theta_std = std(self.theta_q)
        self.theta_avg = average(self.theta_q)
        self.alpha_std = std(self.alpha_q)
        self.alpha_avg = average(self.alpha_q)
        self.beta_std = std(self.beta_q)
        self.beta_avg = average(self.beta_q)
        self.gamma_std = std(self.gamma_q)
        self.gamma_avg = average(self.gamma_q)

    def normalize(self, array, avg, std_dev):
        return average(array)
        #norm = []
        #for a in array:
        #    norm.append((a-avg) / std_dev)
        #return average(norm)

    def record_trigger(self):
        name = raw_input("What is the name of the trigger?")
        for _ in range(self.length):
            sleep(.1)
            self.update_values
        print "Delta = {}".format(self.normalize(self.delta_q, self.delta_avg, self.delta_std))
        print "Theta = {}".format(self.normalize(self.theta_q, self.theta_avg, self.theta_std))
        print "Alpha = {}".format(self.normalize(self.alpha_q, self.alpha_avg, self.alpha_std))
        print "Beta = {}".format(self.normalize(self.beta_q, self.beta_avg, self.beta_std))
        print "Gamma = {}".format(self.normalize(self.gamma_q, self.gamma_avg, self.gamma_std))
        self.output.write("{}\n".format(name))
        self.output.write("Delta={}\n".format(self.normalize(self.delta_q, self.delta_avg, self.delta_std)))
        self.output.write("Theta={}\n".format(self.normalize(self.theta_q, self.theta_avg, self.theta_std)))
        self.output.write("Alpha={}\n".format(self.normalize(self.alpha_q, self.alpha_avg, self.alpha_std)))
        self.output.write("Beta={}\n".format(self.normalize(self.beta_q, self.beta_avg, self.beta_std)))
        self.output.write("Gamma={}\n".format(self.normalize(self.gamma_q, self.gamma_avg, self.gamma_std)))

    def updater(self):
        while not self.quite:
            if not self.recording:
                sleep(.1)
                self.update_values()
                self.calculate_std_dev()

    def run(self):
        while not self.quite:
            command = raw_input("command: ")
            self.parse_command(command)

    def parse_command(self, command):
        command = command.lower()
        if command == "print":
            self.print_recent_values()
        if command == "record":
            self.record_trigger()
        if command == "quit":
            self.close()

    def close(self):
        self.quite = True
        self.output.close()
        self.miner.close()

if __name__=="__main__":
    c = calibrator()
    c.run()
