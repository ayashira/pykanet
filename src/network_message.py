#this class represents a general structure for messages between nodes on the network
#All messages contain the following information:
#  sending username, network address destination, requested action at destination, message content
#some information will be added later : message hash, signature of the message by the user
#A message is converted to an array of bytes when sent on the tcp connection with to_bytes()
#The array of bytes is converted back to a Message class when received with from_bytes()

#TODO : exception handling
class Network_Message():
    message_prefix_size = 4
    subpart_prefix_size = (1, 2, 1, 4)
    
    #username : utf8 string, username of message sender
    #network_path : utf8 string, target address on the network where the message is sent
    #network_command : utf8 string, requested action at the target address
    #message_content : utf8 string, content of the message
    def __init__(self, username=None, network_path=None, network_command=None, message_content=None):
        self.username = username
        self.network_path = network_path
        self.network_command = network_command
        self.message_content = message_content
    
    #we convert each subpart of the message to bytes, and prefix each of them with their length in bytes
    #the complete message is also prefixed with the complete message length
    def to_bytes(self):
        complete_message = b''
        for i, subpart in enumerate( (self.username, self.network_path, self.network_command, self.message_content) ):
            subpart_utf8 = subpart.encode('utf-8')
            complete_message += (len(subpart_utf8)).to_bytes(Network_Message.subpart_prefix_size[i], byteorder='big')
            complete_message += subpart_utf8
        
        complete_message = (len(complete_message)).to_bytes(Network_Message.message_prefix_size, byteorder='big') + complete_message
        
        return complete_message
    
    #read each subpart of the message from a byte encoding
    def from_bytes(self, complete_message):
        start_idx = Network_Message.message_prefix_size
        subpart_list = []
        nb_subparts = len(Network_Message.subpart_prefix_size)
        for i in range(nb_subparts):
            subpart_length = int.from_bytes(complete_message[start_idx:start_idx+Network_Message.subpart_prefix_size[i]], byteorder='big')
            start_idx += Network_Message.subpart_prefix_size[i]
            subpart_list.append( complete_message[start_idx:start_idx+subpart_length].decode('utf-8') )
            start_idx += subpart_length
        
        #initialize the class variables with the message subparts
        self.username, self.network_path, self.network_command, self.message_content = subpart_list

def check_message_equality(message_a, message_b):
    if message_a.username != message_b.username:
        print("FAILED: username")
        return False
    
    if message_a.network_path != message_b.network_path:
        print("FAILED: network_path")
        return False
    
    if message_a.network_command != message_b.network_command:
        print("FAILED: network_command")
        return False
    
    if message_a.message_content != message_b.message_content:
        print("FAILED: message_content")
        return False
        
    return True

#check that we obtain the same message after converting to bytes and converting back from bytes
def check_identity(*message_arguments):
    message_a = Network_Message(*message_arguments)
    message_b = Network_Message()
    message_b.from_bytes( message_a.to_bytes() )
    if check_message_equality(message_a, message_b):
        print("Test... OK")
    
#perform unit tests if the module was not imported
#TODO : more unit tests, especially for exception handling of "bad" messages
if __name__ == '__main__':
    #Test that we obtain the same message after converting to bytes and converting back from bytes
    check_identity("user1", "/user/user1/userpage", "ADD", "A new message from user1")
    check_identity("", "/user/user1/userpage", "ADD", "A new message from user1")
    check_identity("user1", "", "ADD", "A new message from user1")
    check_identity("user1", "/user/user1/userpage", "", "A new message from user1")
    check_identity("user1", "/user/user1/userpage", "ADD", "")
    check_identity("", "", "", "")
