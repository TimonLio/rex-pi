#!/usr/bin/python

import socket
import time

from zeroconf import *

def main():
    service_type = "_ssh._tcp.local."
    service_port = 22
    service_addr = socket.gethostbyname(socket.gethostname())
    service_name = socket.gethostname().replace('.local', '')
    service_name = service_name + '.' + service_type
    print "Register SSH service [%s] on %s ..." % (service_name, service_addr)
    info = ServiceInfo(service_type,
            service_name,
            socket.inet_aton(service_addr), service_port,
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

