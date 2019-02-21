# Server node implementing a chat

from network_message import Network_Message

class Chat_Service():
    
    def __init__(self):
        self.clients = []
        self.content = ""
    
    def add_client(self, new_client):
        #send a message to existing clients
        greetings = str("A new guest is here \^_^/ : ") + new_client.transport.getPeer().host
        message = Network_Message("dummy_user", "/chat/main", "NOTIFICATION", greetings)
        for client in self.clients:
            client.transport.write(message.to_bytes())
        
        #send a message to the new client
        new_client_greetings = self.content
        if len(self.clients) > 0:
            new_client_greetings += str("=====\nCurrently connected guests: ")
            for client in self.clients:
                new_client_greetings += client.transport.getPeer().host + " "
        else:
            new_client_greetings += str("=====\nNo other guest currently connected.")
        
        new_client_greetings += str("\nYou are guest : ") + new_client.transport.getPeer().host
        
        message = Network_Message("dummy_user", "/chat/main", "NOTIFICATION", new_client_greetings)
        
        self.clients.append(new_client)
        print(message.to_bytes())
        new_client.transport.write(message.to_bytes())

    def receive_message(self, sender_client, message):
        #forward the message to all connected clients, add the client name (currently ip address) in front
        message.message_content = sender_client.transport.getPeer().host + " : " + message.message_content
        
        for client in self.clients:
            client.transport.write(message.to_bytes())
        
        #add the new message to the chat history
        self.content += message.message_content + "\n"
   
    def remove_client(self, lost_client):
        self.clients.remove(lost_client)
        
        #message to other clients
        notification_to_send = str("Chat left by ") + lost_client.transport.getPeer().host
        message = Network_Message("dummy_user", "/chat/main", "NOTIFICATION", notification_to_send)
        
        for client in self.clients:
            client.transport.write(message.to_bytes())
