# this is a first test of protocol based on the Twisted library

from __future__ import print_function

from twisted.internet import protocol

class Distributed_protocol(protocol.Protocol):
    
    #called when a new connection is created
    def connectionMade(self):
        #send a message
        self.transport.write(b"hello, world!")
    
    #called when some data is received
    def dataReceived(self, data):
        print("Received data:", data)
        
        #for this test, close the connection immediately
        self.transport.loseConnection()
    
    #called when the connection is lost
    def connectionLost(self, reason):
        print("connection lost")
