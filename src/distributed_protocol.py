# this is a first test of protocol based on the Twisted library

from __future__ import print_function

from twisted.internet import protocol, task

from network_message import Network_Message

from chat_service import *

#main class launching the server services when a connection is made at a given network address
#only one instance of this class is created for one server node (in the server factory)
#this class is the "glue" between connections and services 
class Server_Services():
    
    def __init__(self):
        #dictionary of currently running services dict("address", service)
        #a service is "some code" currently executed, corresponding to a given network address
        self.services_dict = {}
    
    def connection_made(self, client):
        #currently, we do nothing special when a connection is established
        #we wait the first message in order to know what is the target network_path and associated service
        pass

    def receive_message(self, client, message):
        if client.message_receiver_callback:
            client.message_receiver_callback(client, message)
        else:
            print("arrived here")
            #message_receiver not defined yet
            #define it depending on the address in the first message
            if message.network_path.startswith("/chat/"):
                print("chat created")
                client.message_receiver_callback = self.services_dict.setdefault(message.network_path, Chat_Service()).receive_message
                client.connection_lost_callback = self.services_dict.setdefault(message.network_path, Chat_Service()).connection_lost
                client.message_receiver_callback(client, message)
        
    def connection_lost(self, client):
        client.connection_lost_callback(client)

#this class implements the message passing protocol
#one instance of this class is created for each new connection received by the server
class Distributed_protocol(protocol.Protocol):
    #called by Twisted when the connection is created
    def connectionMade(self):
        #disable Nagle's algorithm
        self.transport.setTcpNoDelay(True)
        
        self.transport.setTcpKeepAlive(True)
        
        #bytearray buffer to receive data, initialized as an empty array
        self.receive_buffer = bytearray(b'')
        
        #callbacks to call when messages are received or the connection is lost
        self.message_receiver_callback = None
        self.connection_lost_callback = None        
        
        if self.factory.is_server:
            self.factory.server_services.connection_made(self)
        else:
            self.factory.network_interface.on_connection(self.transport)
            self.activate_keep_alive()
    
    #send a Network_Message to the other end of the connection 
    def send_message(self, message):
        self.transport.write(message.to_bytes())
    
    #called by Twisted when some data is received on the connection
    #transform the raw stream of data into messages, and send the messages to the correct service
    def dataReceived(self, data):
        #add all received data to the buffer
        self.receive_buffer += data
        
        #we need an infinite loop here to process all the already received messages as soon as possible
        #the loop stops when there is no more "complete messages" in the buffer
        #note for later : infinite loop here could be a problem if the buffer contains really a lot of messages
        while True:
            #exit the loop if there is no more message, or if the first 4 bytes (total message length) are not received
            if len(self.receive_buffer) < 4:
                return
            
            #don't forget the 4 initial bytes
            message_length = 4 + int.from_bytes(self.receive_buffer[:4], byteorder='big')
            
            #exit the loop if a complete message is not received yet
            if len(self.receive_buffer) < message_length:
                return
            
            #next_message is received, extract it and remove it from the buffer
            next_message_data = self.receive_buffer[:message_length]
            self.receive_buffer = self.receive_buffer[message_length:]
            
            message = Network_Message()
            message.from_bytes(next_message_data)
            
            #ignore keep-alive messages
            if message.network_command == "KEEP_ALIVE":
                continue
            
            if self.factory.is_server:
                self.factory.server_services.receive_message(self, message)
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
    
    #get the ip address
    def get_host_name(self):
        return self.transport.getPeer().host
    
    #called by Twisted when the connection is lost
    def connectionLost(self, reason):
        if self.factory.is_server:
            print("connection lost")
            self.factory.server_services.connection_lost(self)
