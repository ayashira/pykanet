# This file is a first test of network interface

server_port = 8883

#test on localhost
#server_address = "localhost"

#this is the official first server address
server_address = "31.192.230.58"

from twisted.internet import reactor, protocol

class EchoClient(protocol.Protocol):
    def connectionMade(self):
        #disable Nagle's algorithm
        self.transport.setTcpNoDelay(True)
        
        self.factory.network_interface.on_connection(self.transport)

    def dataReceived(self, data):
        self.factory.network_interface.dataReceived(data)


class EchoClientFactory(protocol.ClientFactory):
    protocol = EchoClient

    def __init__(self, network_interface):
        self.network_interface = network_interface

    def startedConnecting(self, connector):
        print('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.')

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed.')


class NetworkInterface():
    connection = None
    data_received_callback = None
    
    def __init__(self, data_received_callback):
        self.connect_to_server()
        self.data_received_callback = data_received_callback
    
    def network_write(self, data):
        if self.connection:
            self.connection.write(data)
        
    def network_read(self):
        pass

    # =========== private functions ========
    def connect_to_server(self):
        reactor.connectTCP(server_address, server_port, EchoClientFactory(self))
    
    def on_connection(self, connection):
        print("Connected successfully!")
        self.connection = connection

    def dataReceived(self, data):
        self.data_received_callback(data)
