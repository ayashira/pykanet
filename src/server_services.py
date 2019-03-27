
from network_message import NetworkMessage

from apps.login_server import LoginServer
from apps.chat_server import ChatServer
from apps.wiki_server import WikiServer
from apps.turnbasedgame_server import TurnBasedGameServer

class ServerServices():
    '''
        Main class launching the server services when a connection is made at a given network address
        Only one instance of this class is created for one server node (in the server factory)
        This class is the "glue" between connections and services 
    '''
    
    def __init__(self):
        # dictionary of currently running services dict("address", service)
        # a service is "some code" currently executed, corresponding to a given network address
        self.services_dict = {}
    
    def connection_made(self, client):
        # currently, we do nothing special when a connection is established
        # we wait the first message in order to know what is the target network_path and associated service
        pass

    def receive_message(self, client, message):
        if not client.message_receiver_callback:
            # message_receiver not defined yet
            # define it depending on the address in the first message
            if message.network_path.startswith("/login/"):
                # for "login" nodes, we use only one login server for all login addresses
                login_root_address = "/login/"
                if not login_root_address in self.services_dict.keys():
                    print("Login server created")
                    self.services_dict[login_root_address] = LoginServer(login_root_address)
                
                client.message_receiver_callback = self.services_dict[login_root_address].receive_message
                client.connection_lost_callback = self.services_dict[login_root_address].connection_lost
            elif message.network_path.startswith("/chat/"):
                # if the service for this address is not existing yet, it will be created by setdefault
                client.message_receiver_callback = self.services_dict.setdefault(message.network_path, ChatServer(message.network_path)).receive_message
                client.connection_lost_callback = self.services_dict[message.network_path].connection_lost
            elif message.network_path.startswith("/wiki/"):
                # for "wiki" nodes, we use only one wiki server for all wiki addresses
                wiki_root_address = "/wiki/"
                if not wiki_root_address in self.services_dict.keys():
                    self.services_dict[wiki_root_address] = WikiServer(wiki_root_address)
                
                client.message_receiver_callback = self.services_dict[wiki_root_address].receive_message
                client.connection_lost_callback = self.services_dict[wiki_root_address].connection_lost
            elif message.network_path.startswith("/game/"):
                if not message.network_path in self.services_dict.keys() or self.services_dict[message.network_path].service_restart_needed():
                    self.services_dict[message.network_path] = TurnBasedGameServer(message.network_path)
                
                client.message_receiver_callback = self.services_dict[message.network_path].receive_message
                client.connection_lost_callback = self.services_dict[message.network_path].connection_lost
            else:
                # trying to access to a service not defined yet
                client.lose_connection()
                return
            
        # forward the message to the receiver defined for the client
        client.message_receiver_callback(client, message)
        
    def connection_lost(self, client):
        try:
            client.connection_lost_callback(client)
        except:
            # connection lost callback not existing (happens when the client tried to connect to a non-existing service)
            pass
