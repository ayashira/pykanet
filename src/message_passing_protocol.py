
from twisted.internet import protocol, task

from network_message import NetworkMessage
import time

#this class implements the message passing protocol
#one instance of this class is created for each new connection received by the server
class MessagePassingProtocol(protocol.Protocol):
    #called by Twisted when the connection is created
    def connectionMade(self):
        #disable Nagle's algorithm
        self.transport.setTcpNoDelay(True)
        
        self.transport.setTcpKeepAlive(True)
        
        #bytearray buffer to receive data, initialized as an empty array
        self.receive_buffer = bytearray(b'')
        
        #callbacks to call when messages are received or the connection is lost
        #these callbacks are initialized by server_services class in the case of the server-end of a connection
        self.message_receiver_callback = None
        self.connection_lost_callback = None        
        
        self.username = ""
        
        #time of last message
        self.last_message_time = time.monotonic()
        
        if self.factory.is_server:
            self.factory.server_services.connection_made(self)
        else:
            self.factory.network_interface.on_connection(self.transport)
            self.activate_keep_alive()
    
    #send a NetworkMessage to the other end of the connection 
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
            #exit the loop if there is no more message, or if the bytes for the total message length are not received
            if len(self.receive_buffer) < NetworkMessage.MESSAGE_PREFIX_SIZE:
                return
            
            message_length = int.from_bytes(self.receive_buffer[:NetworkMessage.MESSAGE_PREFIX_SIZE], byteorder='big')
            
            #exit the loop if a complete message is not received yet
            if len(self.receive_buffer) < message_length:
                return
            
            #next_message is received, extract it and remove it from the buffer
            next_message_data = self.receive_buffer[:message_length]
            self.receive_buffer = self.receive_buffer[message_length:]
            
            message = NetworkMessage()
            message.from_bytes(next_message_data)
            
            #update the time of the last received message
            self.last_message_time = time.monotonic()
            
            #ignore keep-alive messages
            if message.command == "KEEP_ALIVE":
                continue
            
            #initialize the client name if not already done
            #TODO : this is also here that we will check message signatures
            #       (so that all applications receive only messages with valid signatures)
            if self.username == "":
                self.username = message.username
            
            if self.factory.is_server:
                self.factory.server_services.receive_message(self, message)
            else:
                #case of client end of the connection
                self.factory.network_interface.dataReceived(message)
        
    #activate application-level keep alive messages
    #it needs to be activated for connections to a service that keeps running for a long time
    #typical usage case is a chat service
    def activate_keep_alive(self):
        task_interval_sec = 1.0
        loop_task = task.LoopingCall(self.send_keep_alive)
        loop_task.start(task_interval_sec)
    
    #send a keep-alive message
    def send_keep_alive(self):
        message = NetworkMessage("dummy_address", "KEEP_ALIVE", "")
        self.send_message(message)
    
    #get the ip address
    def get_host_name(self):
        return self.transport.getPeer().host
    
    #return the delay in seconds since the last message
    def last_message_delay(self):
        return time.monotonic() - self.last_message_time
    
    def lose_connection(self):
        self.transport.loseConnection()
    
    #called by Twisted when the connection is lost
    def connectionLost(self, reason):
        if self.factory.is_server:
            self.factory.server_services.connection_lost(self)
