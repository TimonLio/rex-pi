#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import zmq
import json
import time
import uuid
import pickle
import signal
import logging
import threading

logger = logging.getLogger("gardener");
logger.setLevel(logging.DEBUG)


class RaspInfo:
    pass

class Receiver(threading.Thread):
    '''
    Receive and handle messages from ZeroMQ
    '''

    __cv = threading.Condition()

    def __init__(self):
        threading.Thread.__init__(self)
        self.rasp_session_map = {}  # Index by session_id
        self.rasp_uuid_map = {}     # Index by uuid
        self.timer = None

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
        logger.debug("handle message:%s" % message)
        request = json.loads(message)
        response = {}
        response['type'] = request['type']
        if request != None:
            if request['type'] == "REG":
                logger.debug("REG uuid:%s" % request['uuid'])
                session_id = str(uuid.uuid1())
                uid = request['uuid']
                info = self.rasp_uuid_map.get(request['uuid'], None)
                if info != None:
                    session_id = info.session_id
                    logger.debug("REG existed session_id:%s" % session_id)
                else:
                    info = RaspInfo()
                    info.session_id = session_id
                    info.uuid = uid
                    self.rasp_uuid_map[uid] = info
                    self.rasp_session_map[session_id] = info
                    logger.debug("REG assigned session_id:%s" % session_id)
                info.timestamp = time.time()
                response['session_id'] = session_id
                self.reset_timer(session_id)

            if request['type'] == "HEARTBEAT":
                logger.debug("HEARTBEAT session_id:%s" % request['session_id'])
                info = self.rasp_session_map.get(request['session_id'], None)
                if info != None:
                    info.timestamp = time.time()
                    self.reset_timer(request['session_id'])

        return json.dumps(response)

    def reset_timer(self, session_id):
        #logger.debug("reset_timer session_id:%s" % session_id)
        timestamps = []
        for uid in self.rasp_uuid_map.keys():
            info = self.rasp_uuid_map[uid]
            timestamps.append(info.timestamp)

        if self.timer != None:
            self.timer.cancel()
        self.timer = threading.Timer(min(timestamps) + 10 - time.time(), self.on_timeout, [ session_id ])
        self.timer.start()

    def on_timeout(self, session_id):
        logger.debug("on_timeout session_id:%s" % session_id)
        info = self.rasp_session_map[session_id]
        self.rasp_session_map.pop(info.session_id)
        self.rasp_uuid_map.pop(info.uuid)

    def dump(self):
        logger.debug("rasp_uuid_map:%s" % self.rasp_uuid_map)
        logger.debug("rasp_session_map:%s" % self.rasp_session_map)

class ReceiverHelper():
    '''
    Helper class to quit the running daemon
    Sending signal to the persisted pid
    '''
    _conf = "gardener.conf"

    def __init__(self):
        self._data = self._load()

    def set_data(self, key, value):
        self._data[key] = value
        self._save(self._data)

    def get_data(self, key, default):
        return self._data.get(key, default)

    def _save(self, data):
        logger.debug("saving")
        with open(self._conf, 'w') as f:
            pickle.dump(data, f)
        logger.debug("saving data:%s" % repr(self._data))

    def _load(self):
        logger.debug("loading")
        result = {}
        if os.path.isfile(self._conf):
            with open(self._conf, 'r') as f:
                result = pickle.load(f)
            logger.debug("loading data:%s" % repr(result))
        else:
            logger.debug("loading failed")
        return result

    def set_pid(self, pid):
        self.set_data("pid", pid)

    def stop_receiver(self):
        result = False
        pid = self.get_data("pid", None)
        logger.debug("pid:%s" % repr(pid))
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

