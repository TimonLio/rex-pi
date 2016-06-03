#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import zmq
import json
import uuid
import logging

from wakeonlan import wol

logger = logging.getLogger("zmq");
logger.setLevel(logging.DEBUG)


def main():
    logger.debug("main");

    config_path = 'rasp.json'
    config = load_config(config_path)
    config_uuid = config.get('uuid', None);
    config_server = config.get('server', 'localhost')
    config_port_req = config.get('port_req', 5555)
    config_port_sub = config.get('port_sub', 5556)

    if config_uuid == None:
        config_uuid = gen_uuid()
        config['uuid'] = config_uuid
        save_config(config_path, config)

    logger.info("uid:%s" % config_uuid)

    context = zmq.Context()

    reqs = context.socket(zmq.REQ)
    reqs.connect("tcp://%s:%d" % (config_server, config_port_req))

    subs = context.socket(zmq.SUB)
    subs.connect("tcp://%s:%d" % (config_server, config_port_sub))
    subs.setsockopt(zmq.SUBSCRIBE, "")

    request = {}
    request['type'] = "REG"
    request['uuid'] = config_uuid
    reqs.send(json.dumps(request))

    response = reqs.recv()
    logger.debug("response:%s" % response);

    while True:
        handle(subs.recv())

    reqs.close()
    subs.close()

def handle(message):
    macaddr = json.loads(message)
    logger.debug("handle message:%s macaddr:%s" % (message, macaddr));
    wol.send_magic_packet(macaddr)

def gen_uuid():
    return str(uuid.uuid1())

def load_config(config_path):
    config = {}
    logging.info('load config %s' % config_path)
    if os.path.isfile(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    else:
        return config

def save_config(config_path, config):
    logging.info('save config %s' % config_path)
    with open(config_path, 'w') as f:
        json.dump(config, f)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
    main()

