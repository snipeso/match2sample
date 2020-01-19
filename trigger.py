import serial
import time
import logging


class Trigger:
    def __init__(self, serial_device, shouldTrigger, labels={}):
        self.triggerId = 0
        self._delay = 0.01
        self._labels = labels
        print(shouldTrigger)
        if shouldTrigger:
            self._port = serial.Serial(serial_device)

        self.shouldTrigger = shouldTrigger

    def _write(self, n):
        if self.shouldTrigger:
            self._port.write([n])
            time.sleep(self._delay)
            self._port.write([0x00])
        else:
            print("trigger: ", n)

    def send(self, name):
        # TODO: if name not in list, throw error
        self._write(self._labels[name])

    def reset(self):
        self._write(0xFF)

    # def sendID(self, trialID):
    #     if trialID > 249:
    #         raise ValueError(
    #             "Trial ID too large! Can't be larger than 249. You gave:", trialID)

    #     self.send("trialID")
    #     self._write(trialID)

    def sendTriggerId(self):
        currentId = self.triggerId
        logging.info("triggerId: %s", currentId)
        self.triggerId += 1

        # do the thing TODO

        return currentId, 1 * self._delay
