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
    logger.info("main");
    context = zmq.Context()

    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    uid = gen_uuid()
    logger.debug("uid:%s" % uid)

    request = {}
    request['type'] = "REG"
    request['uuid'] = uid
    socket.send(json.dumps(request))

    response = socket.recv()
    logger.info("Received reply %s [ %s ]" % (request, response));

    socket.close()

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

