# this is a first test of protocol based on the Twisted library

from __future__ import print_function

from twisted.internet import protocol

class Distributed_protocol(protocol.Protocol):
    
    #called when a new connection is created
    def connectionMade(self):
        #disable Nagle's algorithm
        self.transport.setTcpNoDelay(True)

        #send a message to existing clients
        greetings = str("A new guest is here \^_^/ : ") + self.transport.getPeer().host
        for client in self.factory.clients:     
            client.transport.write(greetings.encode('utf-8'))
        
        #send a message to the new client
        if len(self.factory.clients) > 0:
            new_client_greetings = str("Already connected guests: ")
            for client in self.factory.clients:
                new_client_greetings += client.transport.getPeer().host + " "
        else:
            new_client_greetings = str("No other guest connected yet.")
        
        new_client_greetings += str("\nYou are guest : ") + self.transport.getPeer().host
        
        self.factory.clients.append(self)
        self.transport.write(new_client_greetings.encode('utf-8'))
    
    #called when some data is received
    def dataReceived(self, data):
        #send the message to all connected clients, add the client name in front
        message_to_send = self.transport.getPeer().host + " : " + data.decode('utf-8')
        for client in self.factory.clients:
            client.transport.write(message_to_send.encode('utf-8'))
        
        print("Received data:", data)
        
        #for this test, close the connection immediately
        #self.transport.loseConnection()
    
    #called when the connection is lost
    def connectionLost(self, reason):
        print("connection lost")
