# This file is a first test of network interface

from twisted.internet import reactor, protocol
from twisted.internet import task

from network_message import NetworkMessage
from message_passing_protocol import MessagePassingProtocol

class NetworkInterface():
    #ip address and port of the first official server
    server_address = "31.192.230.58"
    server_port = 8883
    
    connection = None
    data_received_callback = None
    
    #set localhost as the network address
    #useful for tests on a local machine
    def set_server_to_localhost():
        NetworkInterface.server_address = "localhost"
    
    def __init__(self, data_received_callback, connection_made_callback):
        self.connect_to_server()
        self.data_received_callback = data_received_callback
        self.connection_made_callback = connection_made_callback
    
    #send a message (type: NetworkMessage) to the network
    def send(self, message):
        if self.connection:
            self.connection.write(message.to_bytes())

    # =========== private functions ========
    def connect_to_server(self):
        factory = protocol.ClientFactory()
        factory.protocol = MessagePassingProtocol
        factory.is_server = False
        factory.network_interface = self
        reactor.connectTCP(NetworkInterface.server_address, NetworkInterface.server_port, factory)
    
    def on_connection(self, connection):
        print("Connected successfully!")
        self.connection = connection
        self.connection_made_callback()

    def dataReceived(self, message):
        self.data_received_callback(message)
