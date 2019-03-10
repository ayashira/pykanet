# Server node implementing a chat

from twisted.internet import task
from network_message import Network_Message
from file_manager import File_Manager
import datetime

class ChatServer():
    
    def __init__(self, network_path):
        #list of connected clients
        self.clients = []
        
        #initialize the content with the saved file (if existing) corresponding to the network address
        self.content = File_Manager.file_read(network_path)
        
        self.network_path = network_path
        
        #check regularly that all clients are still active
        task_interval_sec = 20.0
        loop_task = task.LoopingCall(self.remove_inactive_clients)
        loop_task.start(task_interval_sec)
        
    #add a new client to the list of connected clients
    def add_client(self, new_client):
        #send a message to existing clients
        greetings = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + str("  A new guest is here \^_^/ : ") + new_client.get_host_name()
        message = Network_Message(self.network_path, "NOTIFICATION", greetings)
        for client in self.clients:
            client.send_message(message)
        
        #send the current content to the new client
        new_client_greetings = self.content
        message = Network_Message(self.network_path, "APPEND", new_client_greetings)
        new_client.send_message(message)
        
        #send a notification to the new client with the list of currently connected users
        new_client_greetings = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
        if len(self.clients) > 0:
            new_client_greetings += str("  Currently connected guests: ")
            for client in self.clients:
                new_client_greetings += client.get_host_name() + " "
        else:
            new_client_greetings += str("  No other guest currently connected.")
        
        new_client_greetings += str("\nYou are guest : ") + new_client.get_host_name()
        
        message = Network_Message(self.network_path, "NOTIFICATION", new_client_greetings)
        new_client.send_message(message)
        
        self.clients.append(new_client)
    
    #called when a message is received by any of the connected clients
    def receive_message(self, sender_client, message):
        if message.command == "ENTER":
            #a new client asked to enter the room
            #TODO:we should check that he is not already here
            self.add_client(sender_client)
            return
        
        if message.command == "IS_TYPING":
            message.content = sender_client.get_host_name()
            for client in self.clients:
                client.send_message(message)
            return
        
        #forward the message to all connected clients, add the client name (currently ip address) in front
        message.content = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + "  " + sender_client.get_host_name() + " : " + message.content
        
        for client in self.clients:
            client.send_message(message)
        
        #add the new message to the chat history
        self.content += message.content + "\n"
        
        #save the content to disk
        File_Manager.file_append(self.network_path, message.content + "\n")
    
    #called when a client connection is lost
    def connection_lost(self, lost_client):
        self.remove_client(lost_client)
    
    def remove_inactive_clients(self):
        for client in self.clients:
            if client.last_message_delay() > 10.0:
                client.lose_connection()
    
    #remove a client from the list of connected clients
    def remove_client(self, lost_client):
        try:
            self.clients.remove(lost_client)
        except:
            #client already removed
            return
        
        #message to other clients
        notification_to_send = datetime.datetime.now().strftime("%Y-%m-%d, %H:%M:%S") + str("  Chat left by ") + lost_client.get_host_name()
        message = Network_Message(self.network_path, "NOTIFICATION", notification_to_send)
        
        for client in self.clients:
            client.send_message(message)
