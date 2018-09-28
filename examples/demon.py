import threading
import os
import requests
from numpy import *
from time import sleep

import console

class demon(object):
    def __init__(self):
        self.miner = console.data_miner()
        self.miner.start()
        self.updater = threading.Thread(target=self.updater).start()
        self.quite = False
        self.recording = False
        self.added_values = False
        self.threshold = .9
        self.coef = 1.5
        self.config = {}
        input = open(os.path.join(os.curdir, "calib.conf"), "r")
        lines = input.readlines()
        for i in range(len(lines) / 6):
            self.config[lines[i*6]] = {}
            for j in range(1,6):
                parts = lines[(i*6) + j].split("=")
                self.config[lines[i*6]][parts[0]] = float(parts[1])
        #  print self.config
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
        norm = []
        for a in array:
            norm.append((a-avg) / std_dev)
        return average(norm)

    def get_std(self, key):
        if key == "Delta":
            return self.delta_q[-1]
        if key == "Theta":
            return self.theta_q[-1]
        if key == "Alpha":
            return self.alpha_q[-1]
        if key == "Beta":
            return self.beta_q[-1]
        if key == "Gamma":
            return self.gamma_q[-1]

    def remove_triggers(self, triggers, key):
        for trigger in triggers:
            value = self.get_std(key)
            if not (((value / self.config[trigger][key]) >= self.threshold) and ((value / self.config[trigger][key]) <= self.coef*self.threshold)) :
                triggers.remove(trigger)
        return triggers

    def best_match(self, triggers):
        match = 0
        best = 0
        index = -1
        for i, trigger in enumerate(triggers):
            value = self.get_std("Delta")
            match = (value / self.config[trigger]["Delta"])
            value = self.get_std("Theta")
            match += (value / self.config[trigger]["Theta"])
            value = self.get_std("Alpha")
            match += (value / self.config[trigger]["Theta"])
            value = self.get_std("Beta")
            match += (value / self.config[trigger]["Theta"])
            value = self.get_std("Gamma")
            match += (value / self.config[trigger]["Theta"])
            if index == -1 or abs(match - 5) < abs(best-5):
                index = i
                best = match
        return triggers[i]
    
    def check_triggers(self):
        triggers = self.config.keys()
        triggers = self.remove_triggers(triggers, "Delta")
        if triggers:
            triggers = self.remove_triggers(triggers, "Theta")
        if triggers:
            triggers = self.remove_triggers(triggers, "Alpha")
        if triggers:
            triggers = self.remove_triggers(triggers, "Beta")
        if triggers:
            triggers = self.remove_triggers(triggers, "Gamma")
        if triggers:
            print self.best_match(triggers)
            self.send_request(self.best_match(triggers))
            sleep(3)

        
    def updater(self):
        while not self.quite:
            if not self.recording:
                sleep(.1)
                self.update_values()
                self.calculate_std_dev()
                self.check_triggers()

    def run(self):
        while not self.quite:
            command = raw_input("command: ")
            self.parse_command(command)

    def parse_command(self, command):
        command = command.lower()
        if command == "print":
            self.print_recent_values()
        if command == "quit":
            self.close()

    def send_request(self, key):
        key = key.strip()
        url = "http://22.254.10.148/api/v1/key_press/docsis/3438B7842B54/" + key + ":1"
        print url
        print requests.get(url=url).status_code

    def close(self):
        self.quite = True
        self.miner.close()

if __name__=="__main__":
    d = demon()
    d.run()
