# this is a first test of protocol based on the Twisted library

from __future__ import print_function

from twisted.internet import protocol

from network_message import Network_Message

from chat_service import *

#this class implements the message passing protocol
#one instance of this class is created for each new connection received by the server
class Distributed_protocol(protocol.Protocol):
    
    #called when a new connection is created
    def connectionMade(self):
        #disable Nagle's algorithm
        self.transport.setTcpNoDelay(True)
        
        self.transport.setTcpKeepAlive(True)
        
        #bytearray buffer to receive data, initialized as an empty array
        self.receive_buffer = bytearray(b'')
        
        #add the new client to the chat node
        self.factory.services_dict.setdefault("chat_service", Chat_Service()).add_client(self)
            
    #called when some data is received on the connection
    #tranform the raw stream of data into messages, and send the messages to the correct service
    def dataReceived(self, data):
        #add all received data to the buffer
        self.receive_buffer += data
        
        #wait until we receive the first 4 bytes (total message length)
        if len(self.receive_buffer) < 4:
            return
        
        #don't forget the 4 initial bytes
        message_length = 4 + int.from_bytes(self.receive_buffer[:4], byteorder='big')
        
        #wait until we receive the complete message
        if len(self.receive_buffer) < message_length:
            return
        
        #next_message is received, extract it and remove it from the buffer
        next_message_data = self.receive_buffer[:message_length]
        self.receive_buffer = self.receive_buffer[message_length:]
        
        message = Network_Message()
        message.from_bytes(next_message_data)
        
        #ignore keep-alive messages
        if message.network_command == "KEEP_ALIVE":
            return
            
        #send other messages to the ChatNode
        self.factory.services_dict["chat_service"].receive_message(self, message)
    
    #called when the connection is lost
    def connectionLost(self, reason):
        print("connection lost")
        self.factory.services_dict["chat_service"].remove_client(self)
