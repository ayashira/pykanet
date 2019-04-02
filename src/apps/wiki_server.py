from twisted.internet import task
from network_message import NetworkMessage
from file_manager import FileManager
import datetime

class FileChangeLog():
    '''
        Change Log of a file, with change timestamps and usernames
    '''
    
    def __init__(self, filename):
        self.filename = filename
        self.changelog = []
        self.read()
    
    def add_log(self, username):
        idx = len(self.changelog)
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        new_log = [idx, timestamp, username]
        self.changelog.append(new_log)
    
    def read(self):
        log_path = self.filename + ".log"
        if FileManager.file_exists(log_path):
            self.changelog = FileManager.file_read(log_path)
    
    def save(self):
        log_path = self.filename + ".log"
        FileManager.file_write(log_path, self.changelog)
    
    def lastlog_index(self):
        return len(self.changelog) - 1


class WikiServer():
    '''
        Wiki server implementation
    '''
    
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
            # TODO: handle writing errors
            
            # add a new entry to the log file 
            filelog = FileChangeLog(message.network_path)
            filelog.add_log(message.username)
            filelog.save()
            
            # add a new version of the file in the history files
            new_idx = filelog.lastlog_index()
            oldfilename = message.network_path + ".old" + str(new_idx)
            FileManager.file_write(oldfilename, message.content)
            
            # write the new content at the address
            FileManager.file_write(message.network_path, message.content)
            
            # send a message indicating that writing is done
            message = NetworkMessage(message.network_path, "WRITE_DONE", "")
            sender_client.send_message(message)

    # called when a client connection is lost
    def connection_lost(self, lost_client):
        # currently, nothing special to do
        pass
