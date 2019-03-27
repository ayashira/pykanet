from twisted.internet import task
from network_message import NetworkMessage
from file_manager import FileManager
import datetime

class LoginServer():
    '''
        Login server creates new users, and manages storage and retrieval of user keys.
        
        Currently, both user private key and public key are stored on the server.
        
        User private key is encrypted with the user password.
        This means that the user private key can be attacked directly with brute-force attacks.
        TODO: this needs to be improved, because human-chosen passwords are usually much too weak.
    '''
    
    def __init__(self, network_path):
        self.network_path = network_path
        
    # called when a message is received from a client
    def receive_message(self, sender_client, message):
        if message.command == "CREATE":
            # TODO create a new user if not already existing
            pass
        elif message.command == "READ_PUBLIC_KEY":
            # TODO read the public key of an existing user
            pass
        elif message.command == "READ_PRIVATE_KEY":
            # TODO read the private key of an existing user
            pass
    
    # called when a client connection is lost
    def connection_lost(self, lost_client):
        # currently, nothing special to do
        pass
