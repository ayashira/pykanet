# Server node implementing a chat

from twisted.internet import task
from network_message import Network_Message
from file_manager import *
import datetime

class TicTacToe_Service():
    
    def __init__(self, network_path):
        #game state
        self.game_started = False
        self.current_player_id = 0
        
        #list of connected clients
        self.clients = []
        
        #for now, we don' t save anything
        #self.content = File_Manager.file_read(network_path)
        
        self.network_path = network_path
        
        #check regularly that all clients are still active
        task_interval_sec = 20.0
        loop_task = task.LoopingCall(self.remove_inactive_clients)
        loop_task.start(task_interval_sec)

    #called when a message is received by any of the connected clients
    def receive_message(self, sender_client, message):
        print(message.to_bytes())
        if message.network_command == "ENTER":
            #a new client asked to enter the room
            #we allow only two clients for now, the first and the second player
            if len(self.clients) < 2:
                self.add_client(sender_client)
            else:
                sender_client.lose_connection()
            return
        
        if message.network_command == "MOVE":
            if sender_client == self.clients[self.current_player_id]:
                #TODO play move
                
                #next move
                self.current_player_id = (self.current_player_id + 1) % 2
                message = Network_Message("dummy_user", self.network_path, "REQUEST_MOVE", "")
                self.clients[self.current_player_id].send_message(message)
                message = Network_Message("dummy_user", self.network_path, "WAIT_OPP_MOVE", "")
                self.clients[(1 + self.current_player_id) % 2].send_message(message)
            else:
                #someone other than current player tried to play
                pass
     
    #add a new client to the list of connected clients
    def add_client(self, new_client):
        self.clients.append(new_client)
        
        if len(self.clients) == 1:
            #case of the first client (=first player), indicate that we are waiting another player
            message = Network_Message("dummy_user", self.network_path, "WAITING_PLAYER", "")
            new_client.send_message(message)
        elif len(self.clients) == 2:
            #second player is here, we can start the game
            message = Network_Message("dummy_user", self.network_path, "START", "")
            self.clients[0].send_message(message)
            new_client.send_message(message)
            self.game_started = True
            
            self.current_player_id = 0
            message = Network_Message("dummy_user", self.network_path, "REQUEST_MOVE", "")
            self.clients[self.current_player_id].send_message(message)
            message = Network_Message("dummy_user", self.network_path, "WAIT_OPP_MOVE", "")
            self.clients[(1 + self.current_player_id) % 2].send_message(message)
    
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
