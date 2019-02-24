# this is a first test of server using Twisted library

from distributed_protocol import *
from twisted.internet import reactor

port_to_listen = 8883

def main():
    factory = protocol.ServerFactory()
    factory.protocol = Distributed_protocol
    factory.is_server = True
    factory.server_services = Server_Services()
    
    reactor.listenTCP(port_to_listen,factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
