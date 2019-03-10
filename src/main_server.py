# this is a first test of server using Twisted library

from twisted.internet import reactor
from twisted.internet import protocol

from message_passing_protocol import MessagePassingProtocol
from server_services import ServerServices

port_to_listen = 8883

def main():
    factory = protocol.ServerFactory()
    factory.protocol = MessagePassingProtocol
    factory.is_server = True
    factory.server_services = ServerServices()
    
    reactor.listenTCP(port_to_listen,factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
