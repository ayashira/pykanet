from twisted.internet import reactor, protocol
from twisted.internet import task

from network_message import NetworkMessage
from message_passing_protocol import MessagePassingProtocol

class NetworkInterface():
    '''
        Interface to access to the network from clients
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
        self.connect_to_server()
        self.client = client
    
    # send a message (type: NetworkMessage) to the network
    def send(self, message):
        if self.connection:
            self.connection.write(message.to_bytes())
    
    def lose_connection(self):
        if self.connection:
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
        self.client.connection_made()
    
    def dataReceived(self, message):
        self.client.receive_message(message)
