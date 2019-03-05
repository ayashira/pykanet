# this is a first test of protocol based on the Twisted library

from network_message import Network_Message

from apps.chat_server import *
from apps.turnbasedgame_service import *

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
        if not client.message_receiver_callback:
            #message_receiver not defined yet
            #define it depending on the address in the first message
            if message.network_path.startswith("/chat/"):
                #if the service for this address is not existing yet, it will be created by setdefault
                client.message_receiver_callback = self.services_dict.setdefault(message.network_path, Chat_Service(message.network_path)).receive_message
                client.connection_lost_callback = self.services_dict[message.network_path].connection_lost
            elif message.network_path.startswith("/game/"):
                if not message.network_path in self.services_dict.keys() or self.services_dict[message.network_path].service_restart_needed():
                    self.services_dict[message.network_path] = TurnBasedGame_Service(message.network_path)
                
                client.message_receiver_callback = self.services_dict[message.network_path].receive_message
                client.connection_lost_callback = self.services_dict[message.network_path].connection_lost
            else:
                #trying to access to a service not defined yet
                client.lose_connection()
                return
            
        #forward the message to the receiver defined for the client
        client.message_receiver_callback(client, message)
        
    def connection_lost(self, client):
        try:
            client.connection_lost_callback(client)
        except:
            #connection lost callback not existing (happens when the client tried to connect to a non-existing service)
            pass
