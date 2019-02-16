# this is a first test of client based on the Twisted library

from distributed_protocol import *
from twisted.internet import reactor

server_port = 8883
server_address = "localhost"

# this connects the protocol to a server running at a specified address/port
def main():
    factory = protocol.ClientFactory()
    factory.protocol = Distributed_protocol
    reactor.connectTCP(server_address, server_port, factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
