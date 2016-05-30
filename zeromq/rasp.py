#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import zmq
import json
import uuid
import logging

logger = logging.getLogger("zmq");
logger.setLevel(logging.DEBUG)


def main():
    logger.debug("main");
    context = zmq.Context()

    reqs = context.socket(zmq.REQ)
    reqs.connect("tcp://localhost:5555")

    subs = context.socket(zmq.SUB)
    subs.connect("tcp://localhost:5556")
    subs.setsockopt(zmq.SUBSCRIBE, "")

    uid = gen_uuid()
    logger.info("uid:%s" % uid)

    request = {}
    request['type'] = "REG"
    request['uuid'] = uid
    reqs.send(json.dumps(request))

    response = reqs.recv()
    logger.debug("response:%s" % response);

    #poller = zmq.Poller()
    #poller.register(reqs, zmq.POLLIN)
    #poller.register(subs, zmq.POLLIN)

    while True:
        handle(subs.recv())

    reqs.close()
    subs.close()

def handle(message):
    logger.debug("handle message:%s" % message);
    pass

def gen_uuid():
    if os.path.isfile('rasp.conf'):
        with open('rasp.conf', 'r') as f:
            cache = json.load(f)
            uid = cache['uuid']
    else:
        uid = uuid.uuid1()
        cache = {}
        cache['uuid'] = str(uid)
        with open('rasp.conf', 'w') as f:
            json.dump(cache, f)
    return uid

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
    main()

