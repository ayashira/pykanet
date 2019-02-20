#this class represents a general structure for messages between nodes on the network
#All messages contain the following information:
#  sending username, network address destination, requested action at destination, message content
#some information will be added later : message hash, signature of the message by the user
#A message is converted to an array of bytes when sent on the tcp connection with to_bytes()
#The array of bytes is converted back to a Message class when received with from_bytes()

#TODO : exception handling
class Network_Message():
    #username : utf8 string, username of message sender
    #network_path : utf8 string, target address on the network where the message is sent
    #network_command : utf8 string, requested action at the target address
    #message_content : utf8 string, content of the message
    def __init__(self, username=None, network_path=None, network_command=None, message_content=None):
        self.username = username
        self.network_path = network_path
        self.network_command = network_command
        self.message_content = message_content
    
    #we convert each element of the message to bytes, and prefix them with the number of bytes after conversion
    #the complete message is also prefixed with the complete message length
    def to_bytes(self):
        username_utf8 = self.username.encode('utf-8')
        complete_message = (len(username_utf8)).to_bytes(1, byteorder='big')
        complete_message += username_utf8
        
        network_path_utf8 = self.network_path.encode('utf-8')
        complete_message += (len(network_path_utf8)).to_bytes(2, byteorder='big')
        complete_message += network_path_utf8
        
        network_command_utf8 = self.network_command.encode('utf-8')
        complete_message += (len(network_command_utf8)).to_bytes(1, byteorder='big')
        complete_message += network_command_utf8
        
        message_content_utf8 = self.message_content.encode('utf-8')
        complete_message += (len(message_content_utf8)).to_bytes(4, byteorder='big')
        complete_message += message_content_utf8
        
        complete_message = (len(complete_message)).to_bytes(4, byteorder='big') + complete_message
        
        return complete_message
        
    def from_bytes(self, complete_message):
        start_idx = 4
        username_length = int.from_bytes(complete_message[start_idx:start_idx+1], byteorder='big')
        self.username = complete_message[start_idx+1:start_idx+1+username_length].decode('utf-8')
        start_idx += 1 + username_length
        
        network_path_length = int.from_bytes(complete_message[start_idx:start_idx+2], byteorder='big')
        self.network_path = complete_message[start_idx+2:start_idx+2+network_path_length].decode('utf-8') 
        start_idx += 2 + network_path_length
        
        network_command_length = int.from_bytes(complete_message[start_idx:start_idx+1], byteorder='big')
        self.network_command = complete_message[start_idx+1:start_idx+1+network_command_length].decode('utf-8')
        start_idx += 1 + network_command_length
        
        network_content_length = int.from_bytes(complete_message[start_idx:start_idx+4], byteorder='big')
        self.message_content = complete_message[start_idx+4:start_idx+4+network_content_length].decode('utf-8')
        start_idx += 4 + network_content_length

#perform unit tests if the module was not imported
#TODO : more unit tests, especially for exception handling of "bad" messages
if __name__ == '__main__':
    message_test = Network_Message("user1", "/user/user1/userpage", "ADD", "A new message from user1")
    message_copy = Network_Message()
    message_copy.from_bytes( message_test.to_bytes() )
    if message_copy.username != message_test.username:
        print("FAILED: username")
    else:
        print("OK: username")
        
    if message_copy.network_path != message_test.network_path:
        print("FAILED: network_path")
    else:
        print("OK: network_path")

    if message_copy.network_command != message_test.network_command:
        print("FAILED: network_command")
    else:
        print("OK: network_command")

    if message_copy.message_content != message_test.message_content:
        print("FAILED: message_content")
    else:
        print("OK: message_content")
