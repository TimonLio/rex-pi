#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import zmq
import json
import pickle
import logging
import threading

logger = logging.getLogger("gardener");
logger.setLevel(logging.DEBUG)

class Receiver(threading.Thread):
    '''
    Receive and handle messages from ZeroMQ
    '''

    __cv = threading.Condition()

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        logger.debug("running+")
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5555")
        while True:
            socket.send(self.handle(socket.recv()))
        socket.close()
        logger.debug("running-")

    def handle(self, message):
        logger.debug("handle_message {}".format(message))
        request = json.loads(message)
        response = {}
        if request != None:
            if request['type'] == "REG":
                logger.debug("REG uuid:%s" % request['uuid'])

            response['type'] = "REG"
            response['uuid'] = request['uuid']
            response['response'] = 0
        return json.dumps(response)

class ReceiverHelper():
    '''
    Helper class to quit the running daemon
    Sending signal to the persisted pid
    '''
    _conf = "gardener.conf"

    def __init__(self):
        self.data = {}

    def set_data(self, key, value):
        self.data[key] = value

    def get_data(self, key, default):
        if key in self.data:
            return self.data[key]
        return default

    def set_pid(self, pid):
        self.set_data("pid", pid)

    def stop_receiver(self):
        result = False
        pid = self.get_data("pid", None)
        if pid != None and pid > 0:
            try:
                os.kill(pid, signal.SIGKILL)
                result = True
            except OSError:
                pass
        else:
            logger.warn("PID not found, can't kill it")
        return result

def sig_handler(signum, frame):
    logger.info("Signal handler called with signal:%d" % (signum))

# TODO: Let the thread can quit nicely
# TODO: How to use sig_handler
def main():
    logger.info("main");
    helper = ReceiverHelper()
    arg = len(sys.argv) > 1 and sys.argv[1] or ""
    if arg.find("start") > -1:
        logger.info("Start receiver")
        helper.set_pid(os.getpid())
        receiver = Receiver()
        receiver.start()
        return
    if arg.find("stop") > -1:
        logger.info("Stop receiver")
        helper.stop_receiver()
        return

    print """\
        Usage: gardener [OPTIONS]
            start       Start the daemon
            stop        Stop the daemon
        """

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
    main()

