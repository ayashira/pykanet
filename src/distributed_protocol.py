# this is a first test of protocol based on the Twisted library

from __future__ import print_function

from twisted.internet import protocol

from network_message import Network_Message

class Distributed_protocol(protocol.Protocol):
    
    #called when a new connection is created
    def connectionMade(self):
        #disable Nagle's algorithm
        self.transport.setTcpNoDelay(True)
        
        self.transport.setTcpKeepAlive(True)

        #send a message to existing clients
        greetings = str("A new guest is here \^_^/ : ") + self.transport.getPeer().host
        message = Network_Message("dummy_user", "/chat/main", "NOTIFICATION", greetings)
        for client in self.factory.clients:
            client.transport.write(message.to_bytes())
        
        #send a message to the new client
        new_client_greetings = self.factory.content
        if len(self.factory.clients) > 0:
            new_client_greetings += str("=====\nCurrently connected guests: ")
            for client in self.factory.clients:
                new_client_greetings += client.transport.getPeer().host + " "
        else:
            new_client_greetings += str("=====\nNo other guest currently connected.")
        
        new_client_greetings += str("\nYou are guest : ") + self.transport.getPeer().host
        
        message = Network_Message("dummy_user", "/chat/main", "NOTIFICATION", new_client_greetings)
        
        self.factory.clients.append(self)
        print(message.to_bytes())
        self.transport.write(message.to_bytes())
    
    #called when some data is received
    def dataReceived(self, data):
        message = Network_Message()
        message.from_bytes(data)
        
        #ignore keep-alive messages
        if message.network_command == "KEEP_ALIVE":
            return
        
        
        #send the message to all connected clients, add the client name in front
        message.message_content = self.transport.getPeer().host + " : " + message.message_content
        
        for client in self.factory.clients:
            client.transport.write(message.to_bytes())
        
        print("Received data:", data)
        
        #add the new message to the chat history
        self.factory.content += message.message_content + "\n"
    
    #called when the connection is lost
    def connectionLost(self, reason):
        print("connection lost")
        self.factory.clients.remove(self)
        
        #message to other clients
        notification_to_send = str("Chat left by ") + self.transport.getPeer().host
        message = Network_Message("dummy_user", "/chat/main", "NOTIFICATION", notification_to_send)
        
        for client in self.factory.clients:
            client.transport.write(message.to_bytes())
