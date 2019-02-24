# Server node implementing a chat

from network_message import Network_Message

class Chat_Service():
    
    def __init__(self):
        self.clients = []
        self.content = ""
    
    #called when a new client connection is opened
    def add_client(self, new_client):
        #send a message to existing clients
        greetings = str("A new guest is here \^_^/ : ") + new_client.get_host_name()
        message = Network_Message("dummy_user", "/chat/main", "NOTIFICATION", greetings)
        for client in self.clients:
            client.send_message(message)
        
        #send a message to the new client
        new_client_greetings = self.content
        if len(self.clients) > 0:
            new_client_greetings += str("=====\nCurrently connected guests: ")
            for client in self.clients:
                new_client_greetings += client.get_host_name() + " "
        else:
            new_client_greetings += str("=====\nNo other guest currently connected.")
        
        new_client_greetings += str("\nYou are guest : ") + new_client.get_host_name()
        
        message = Network_Message("dummy_user", "/chat/main", "NOTIFICATION", new_client_greetings)
        
        self.clients.append(new_client)
        #print(message.to_bytes())
        new_client.send_message(message)
    
    #called when a message is received by any of the connected clients
    def receive_message(self, sender_client, message):
        if message.network_command == "CONNECT":
            self.add_client(sender_client)
            return
        
        #forward the message to all connected clients, add the client name (currently ip address) in front
        message.message_content = sender_client.get_host_name() + " : " + message.message_content
        
        for client in self.clients:
            client.send_message(message)
        
        #add the new message to the chat history
        self.content += message.message_content + "\n"
    
    #called when a client connection is lost
    def connection_lost(self, lost_client):
        self.remove_client(lost_client)
        
    #remove a client from the list of connected clients
    def remove_client(self, lost_client):
        self.clients.remove(lost_client)
        
        #message to other clients
        notification_to_send = str("Chat left by ") + lost_client.get_host_name()
        message = Network_Message("dummy_user", "/chat/main", "NOTIFICATION", notification_to_send)
        
        for client in self.clients:
            client.send_message(message)
