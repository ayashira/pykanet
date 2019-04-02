from twisted.internet import task
from network_message import NetworkMessage
from file_manager import FileManager

from date_utils import DateUtil

class ChatServer():
    '''
        Chat server implementation
    '''
    
    def __init__(self, network_path):
        # list of connected clients
        self.clients = []
        
        # initialize the content with the saved file (if existing) corresponding to the network address
        if FileManager.file_exists(network_path):
            self.content = FileManager.file_read(network_path)
        else:
            self.content = []
        
        self.network_path = network_path
        
        # check regularly that all clients are still active
        task_interval_sec = 20.0
        loop_task = task.LoopingCall(self.remove_inactive_clients)
        loop_task.start(task_interval_sec)
        
    # add a new client to the list of connected clients
    def add_client(self, new_client):
        # send a message to existing clients
        greetings = [DateUtil.utcnow(), new_client.username]
        message = NetworkMessage(self.network_path, "NOTIFICATION_NEW_CLIENT", greetings)
        for client in self.clients:
            client.send_message(message)
        
        # send the current content to the new client
        new_client_greetings = self.content
        message = NetworkMessage(self.network_path, "INIT_CONTENT", new_client_greetings)
        new_client.send_message(message)
        
        # send a notification to the new client with the list of currently connected users
        new_client_greetings = [DateUtil.utcnow()]
        if len(self.clients) > 0:
            for client in self.clients:
                new_client_greetings.append(client.username)
        message = NetworkMessage(self.network_path, "NOTIFICATION_CLIENT_LIST", new_client_greetings)
        new_client.send_message(message)
        
        self.clients.append(new_client)
    
    # called when a message is received by any of the connected clients
    def receive_message(self, sender_client, message):
        if message.command == "ENTER":
            # a new client asked to enter the room
            # TODO:we should check that he is not already here
            self.add_client(sender_client)
            return
        
        if message.command == "IS_TYPING":
            message.content = sender_client.username
            for client in self.clients:
                client.send_message(message)
            return
        
        # forward the time, username and message to all connected clients
        message.content = [DateUtil.utcnow(), sender_client.username, message.content]
        
        for client in self.clients:
            client.send_message(message)
        
        # add the new message to the chat history
        self.content.append(message.content)
        
        # save the content to disk
        FileManager.file_write(self.network_path, self.content)
    
    # called when a client connection is lost
    def connection_lost(self, lost_client):
        self.remove_client(lost_client)
    
    def remove_inactive_clients(self):
        for client in self.clients:
            if client.last_message_delay() > 10.0:
                client.lose_connection()
    
    # remove a client from the list of connected clients
    def remove_client(self, lost_client):
        try:
            self.clients.remove(lost_client)
        except:
            # client already removed
            return
        
        # message to other clients
        notification_to_send = [DateUtil.utcnow(), lost_client.username]
        message = NetworkMessage(self.network_path, "NOTIFICATION_CLIENT_LEFT", notification_to_send)
        
        for client in self.clients:
            client.send_message(message)
