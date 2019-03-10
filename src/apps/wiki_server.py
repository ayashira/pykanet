# Server node implementing wiki pages

from twisted.internet import task
from network_message import Network_Message
from file_manager import File_Manager
import datetime

class WikiServer():
    
    def __init__(self, network_path):
        #initialize the content with the saved file (if existing) corresponding to the network address
        #self.content = File_Manager.file_read(network_path)
        
        self.network_path = network_path
        
    #called when a message is received from a client
    def receive_message(self, sender_client, message):
        if message.command == "READ":
            #return the content of the requested address (if existing)
            #TODO: handle non-existing files with specific message
            page_content = File_Manager.file_read(message.network_path)            
            message.command = "READ_RESULT"
            message.message_content = page_content
            sender_client.send_message(message)
        elif message.command == "WRITE":
            #write the new content at the address
            File_Manager.file_write(message.network_path, message.message_content)
            
            #send a message indicating that writing is done
            #TODO: handle writing errors
            #TODO: write history
            message = Network_Message(message.network_path, "WRITE_DONE", "")
            sender_client.send_message(message)

    #called when a client connection is lost
    def connection_lost(self, lost_client):
        #currently, nothing special to do
        pass
