# Server node implementing wiki pages

from twisted.internet import task
from network_message import NetworkMessage
from file_manager import FileManager
import datetime

class WikiServer():
    
    def __init__(self, network_path):
        self.network_path = network_path
        
    # called when a message is received from a client
    def receive_message(self, sender_client, message):
        if message.command == "READ":
            # return the content of the requested address
            if FileManager.file_exists(message.network_path):
                page_content = FileManager.file_read(message.network_path)            
                message.command = "READ_RESULT"
                message.content = page_content
            else:
                # specific message when the page does not exist yet
                message.command = "NOT_EXISTING"
                message.content = ""
            sender_client.send_message(message)
        elif message.command == "WRITE":
            # write the new content at the address
            FileManager.file_write(message.network_path, message.content)
            
            # send a message indicating that writing is done
            #TODO: handle writing errors
            #TODO: write history
            message = NetworkMessage(message.network_path, "WRITE_DONE", "")
            sender_client.send_message(message)

    # called when a client connection is lost
    def connection_lost(self, lost_client):
        # currently, nothing special to do
        pass
