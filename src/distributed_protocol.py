# this is a first test of protocol based on the Twisted library

from __future__ import print_function

from twisted.internet import protocol, task

from network_message import Network_Message

from chat_service import *

#this class implements the message passing protocol
#one instance of this class is created for each new connection received by the server
class Distributed_protocol(protocol.Protocol):
    
    #currently running services
    services_dict = {}
    
    #called by Twisted when the connection is created
    def connectionMade(self):
        #disable Nagle's algorithm
        self.transport.setTcpNoDelay(True)
        
        self.transport.setTcpKeepAlive(True)
        
        #bytearray buffer to receive data, initialized as an empty array
        self.receive_buffer = bytearray(b'')
        
        if self.factory.is_server:
            #add the new client to the chat node
            Distributed_protocol.services_dict.setdefault("chat_service", Chat_Service()).add_client(self)
        else:
            self.factory.network_interface.on_connection(self.transport)
            self.activate_keep_alive()
    
    #send a Network_Message to the other end of the connection 
    def send_message(self, message):
        self.transport.write(message.to_bytes())
    
    #called by Twisted when some data is received on the connection
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
            
        if self.factory.is_server:
            #send other messages to the ChatNode
            Distributed_protocol.services_dict["chat_service"].receive_message(self, message)
        else:
            #case of client end of the connection
            self.factory.network_interface.dataReceived(message)
        
    #activate application-level keep alive messages
    #it needs to be activated for connections to a service that keeps running for a long time
    #typical usage case is a chat service
    def activate_keep_alive(self):
        loop_task = task.LoopingCall(self.send_keep_alive)
        loop_task.start(1.0) # call every 1 second
    
    #send a keep-alive message
    def send_keep_alive(self):
        message = Network_Message("dummy_user", "dummy_address", "KEEP_ALIVE", "")
        self.send_message(message)
    
    #called by Twisted when the connection is lost
    def connectionLost(self, reason):
        if self.factory.is_server:
            print("connection lost")
            Distributed_protocol.services_dict["chat_service"].remove_client(self)
