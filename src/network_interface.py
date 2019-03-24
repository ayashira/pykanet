from twisted.internet import reactor, protocol
from twisted.internet import task

from network_message import NetworkMessage
from message_passing_protocol import MessagePassingProtocol

import random

class NetworkInterface():
    '''
        Interface to access the network from a client
    '''
    
    # ip address and port of the first official server
    server_address = "31.192.230.58"
    server_port = 8883
    
    use_local_host = False
    
    # set localhost as the network address
    # useful for tests on a local machine
    def set_server_to_localhost():
        NetworkInterface.use_local_host = True
    
    def __init__(self, client):
        self.connection = None
        self.connect_to_server()
        self.pending_message_list = []
        self.client = client
    
    # send a message (type: NetworkMessage) to the network
    def send(self, network_path, command, content):
        message = NetworkMessage(network_path, command, content)
        if self.connection is not None:
            self.connection.write(message.to_bytes())
        else:
            # wait until the connection is established
            self.pending_message_list.append(message.to_bytes())
    
    def lose_connection(self):
        if self.connection is not None:
            self.connection.loseConnection()
    
    # =========== private functions ========
    def connect_to_server(self):
        factory = protocol.ClientFactory()
        factory.protocol = MessagePassingProtocol
        factory.is_server = False
        factory.network_interface = self
        
        if NetworkInterface.use_local_host:
            reactor.connectTCP("localhost", NetworkInterface.server_port, factory)
        else:
            reactor.connectTCP(NetworkInterface.server_address, NetworkInterface.server_port, factory)
    
    def on_connection(self, connection):
        print("Connected successfully!")
        self.connection = connection
        
        # send all pending messages
        for msg in self.pending_message_list:
            self.connection.write(msg)
        self.pending_message_list = []
    
    # called by MessagePassingProtocol.dataReceived when a message is received
    # transmit the message to the correct local client
    def receive_message(self, message):
        self.client.receive_message(message)
