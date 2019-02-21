# This file is a first test of network interface

server_port = 8883

#test on localhost
#server_address = "localhost"

#this is the official first server address
server_address = "31.192.230.58"

from twisted.internet import reactor, protocol
from twisted.internet import task

from network_message import Network_Message

class EchoClient(protocol.Protocol):
    def connectionMade(self):
        #disable Nagle's algorithm
        self.transport.setTcpNoDelay(True)
        
        self.transport.setTcpKeepAlive(True)
        
        self.factory.network_interface.on_connection(self.transport)
        
        #application-level keep alive messages
        loop_task = task.LoopingCall(self.sendKeepAlive)
        loop_task.start(1.0) # call every 1 second
        
    def dataReceived(self, data):
        #print(data)
        message = Network_Message()
        message.from_bytes(data)
        self.factory.network_interface.dataReceived(message)
        
    def sendKeepAlive(self):
        message = Network_Message("dummy_user", "dummy_address", "KEEP_ALIVE", "")
        self.transport.write(message.to_bytes())


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
    
    #send a message (type: Network_Message) to the network
    def network_send(self, message):
        if self.connection:
            self.connection.write(message.to_bytes())

    # =========== private functions ========
    def connect_to_server(self):
        reactor.connectTCP(server_address, server_port, EchoClientFactory(self))
    
    def on_connection(self, connection):
        print("Connected successfully!")
        self.connection = connection

    def dataReceived(self, message):
        self.data_received_callback(message)
