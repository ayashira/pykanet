from twisted.internet import task
from network_message import NetworkMessage
from file_manager import FileManager
import datetime
import random

from apps.turnbasedgame_list import TurnBasedGameList

class TurnBasedGameServer():
    '''
        turned-based game server implementation
    '''
    
    def __init__(self, network_path):
        # game state
        self.game_started = False
        self.game_ended = False
        self.current_player_id = 0
        
        # list of connected clients
        self.clients = []
        
        # for now, we don' t save anything
        #self.content = FileManager.file_read(network_path)
        
        self.network_path = network_path
        
        # check regularly that all clients are still active
        task_interval_sec = 20.0
        loop_task = task.LoopingCall(self.remove_inactive_clients)
        loop_task.start(task_interval_sec)
        
        # set the target game, depending on the game name
        self.target_game = TurnBasedGameList.get_game_from_name(network_path)
    
    # called when a message is received from any of the connected clients
    def receive_message(self, sender_client, message):
        if message.command == "ENTER":
            # a new client asked to enter the room
            # we allow only two clients for now, the first and the second player
            if len(self.clients) < 2:
                self.add_client(sender_client)
            else:
                sender_client.lose_connection()
        
        elif message.command == "MOVE":
            if sender_client == self.clients[self.current_player_id]:
                [time, move] = message.content
                if not self.target_game.is_valid_play(move, player = self.current_player_id + 1):
                    # move not valid, don't do anything. TODO : request a move again
                    return
                
                # move is valid, play it, and indicate the value to both players
                self.target_game.play(move, player = self.current_player_id + 1)
                if self.current_player_id == 0:
                    command = "PLAYER1_MOVE"

                else:
                    command = "PLAYER2_MOVE"
                
                message = NetworkMessage(self.network_path, command, move)
                for client in self.clients:
                    client.send_message(message)
                
                # check if the game is finished
                winner = self.target_game.winner()
                if winner != -1:
                    command = "GAME_FINISHED"
                    message = NetworkMessage(self.network_path, command, winner)
                    for client in self.clients:
                        client.send_message(message)
                        
                        # end the connection
                        client.lose_connection()
                    
                    self.game_ended = True
                    return
                
                # check which player is next in the game (in some games, the same player can play again)
                self.current_player_id = self.target_game.get_current_player() - 1
                self.opp_player_id = 0 if self.current_player_id == 1 else 1
                
                # request next move
                message = NetworkMessage(self.network_path, "REQUEST_MOVE", time)
                self.clients[self.current_player_id].send_message(message)
                message = NetworkMessage(self.network_path, "WAIT_OPP_MOVE", time)
                self.clients[self.opp_player_id].send_message(message)
            else:
                # someone other than current player tried to play
                # TODO: error handling
                pass
        
        elif message.command == "TIMEOUT":
            command = "GAME_FINISHED"
            winner = self.opp_player_id + 1
            message = NetworkMessage(self.network_path, command, winner)
            for client in self.clients:
                client.send_message(message)
                client.lose_connection()
            self.game_ended = True
    
    # add a new client to the list of connected clients
    def add_client(self, new_client):
        self.clients.append(new_client)
        
        if len(self.clients) == 1:
            # case of the first client (=first player), indicate that we are waiting another player
            message = NetworkMessage(self.network_path, "WAITING_PLAYER", "")
            new_client.send_message(message)
        elif len(self.clients) == 2:
            # second player is here, we can start the game
            message = NetworkMessage(self.network_path, "START", "")
            self.clients[0].send_message(message)
            new_client.send_message(message)
            self.game_started = True

            self.current_player_id = 0
            self.opp_player_id = 1
            
            # to determine first player at random
            first_player = random.randrange(2)
            second_player = 1 if first_player == 0 else 0
            
            # change the order of the clients if second player was chosen to play first
            if first_player == 1:
                self.clients = self.clients[::-1]

            usernames = [self.clients[idx].username for idx in range(2)]

            message = NetworkMessage(self.network_path, "SET_PLAYER_ID", "1")
            self.clients[0].send_message(message)
            message = NetworkMessage(self.network_path, "REQUEST_MOVE", "")
            self.clients[self.current_player_id].send_message(message)
            # send usernames to client
            message = NetworkMessage(self.network_path, "SET_USER_NAMES", usernames)
            self.clients[self.current_player_id].send_message(message)
            
            message = NetworkMessage(self.network_path, "SET_PLAYER_ID", "2")
            self.clients[1].send_message(message)
            message = NetworkMessage(self.network_path, "WAIT_OPP_MOVE", "")
            self.clients[self.opp_player_id].send_message(message)
            
            message = NetworkMessage(self.network_path, "SET_USER_NAMES", usernames[::-1])
            self.clients[self.opp_player_id].send_message(message)
    
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
        
        # end the game if both clients are disconnected
        # TODO : case of only one client disconnection during a game
        if len(self.clients) == 0:
            self.game_ended = True
        
    # restart of service is needed when the game is finished
    def service_restart_needed(self):
        return self.game_ended
