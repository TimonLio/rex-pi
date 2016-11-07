#!/usr/bin/python

import socket
import time

from zeroconf import *

def main():
    print "Register SSH service ..."

    service_type = "_ssh._tcp.local."
    info = ServiceInfo(service_type,
            "RPi3." + service_type,
            socket.inet_aton("127.0.0.1"), 22,
            0, 0, "", None)

    zc = Zeroconf()
    zc.register_service(info)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print("Unregistering ...")
        zc.unregister_service(info)
        zc.close()

if __name__ == '__main__':
    main()

