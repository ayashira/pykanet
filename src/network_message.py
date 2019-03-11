from user_utils import MainUser

#this class represents a general structure for messages between nodes on the network
#All messages contain the following information:
#  message encoding version
#  sending username
#  network address destination
#  requested action at destination
#  message content
#some information will be added later : message hash, signature of the message by the user
#A message is converted to an array of bytes when sent on the tcp connection with to_bytes()
#The array of bytes is converted back to a Message class when received with from_bytes()

#TODO : exception handling
class NetworkMessage():
    #constants defining the version and the number of bytes used for prefixing the length
    #the number of bytes used for the length put a limit of 2^(nb bytes) on each subpart
    MESSAGE_VERSION = 0
    MESSAGE_PREFIX_SIZE = 4
    SUBPART_PREFIX_SIZE = (1, 2, 1, 4)
    
    #username : utf8 string, username of message sender
    #network_path : utf8 string, target address on the network where the message is sent
    #command : utf8 string, requested action at the target address
    #content : utf8 string, content of the message
    def __init__(self, network_path=None, command=None, content=None):
        self.username = MainUser.username
        self.network_path = network_path
        self.command = command
        self.content = content
    
    #we convert each subpart of the message to bytes, and prefix each of them with their length in bytes
    #the complete message is also prefixed with the complete message length
    def to_bytes(self):
        complete_message = bytearray(b'')
        
        #reserve the space for the message total length
        complete_message += int(0).to_bytes(NetworkMessage.MESSAGE_PREFIX_SIZE, byteorder='big')
        
        #message encoding version
        complete_message += int(NetworkMessage.MESSAGE_VERSION).to_bytes(2, byteorder='big')
        
        #each subpart prefixed by its length
        for i, subpart in enumerate( (self.username, self.network_path, self.command, self.content) ):
            subpart_utf8 = subpart.encode('utf-8')
            complete_message += (len(subpart_utf8)).to_bytes(NetworkMessage.SUBPART_PREFIX_SIZE[i], byteorder='big')
            complete_message += subpart_utf8
        
        #initialize the total message length at the beginning of the message
        complete_message[:NetworkMessage.MESSAGE_PREFIX_SIZE] = (len(complete_message)).to_bytes(NetworkMessage.MESSAGE_PREFIX_SIZE, byteorder='big')
        
        return complete_message
    
    #read each subpart of the message from a byte encoding
    def from_bytes(self, complete_message):
        start_idx = NetworkMessage.MESSAGE_PREFIX_SIZE
        version = int.from_bytes(complete_message[start_idx:start_idx+2], byteorder='big')
        start_idx += 2
        
        subpart_list = []
        nb_subparts = len(NetworkMessage.SUBPART_PREFIX_SIZE)
        for i in range(nb_subparts):
            subpart_length = int.from_bytes(complete_message[start_idx:start_idx+NetworkMessage.SUBPART_PREFIX_SIZE[i]], byteorder='big')
            start_idx += NetworkMessage.SUBPART_PREFIX_SIZE[i]
            subpart_list.append( complete_message[start_idx:start_idx+subpart_length].decode('utf-8') )
            start_idx += subpart_length
        
        #initialize the class variables with the message subparts
        self.username, self.network_path, self.command, self.content = subpart_list

def check_message_equality(message_a, message_b):
    if message_a.username != message_b.username:
        print("FAILED: username")
        return False
    
    if message_a.network_path != message_b.network_path:
        print("FAILED: network_path")
        return False
    
    if message_a.command != message_b.command:
        print("FAILED: command")
        return False
    
    if message_a.content != message_b.content:
        print("FAILED: content")
        return False
        
    return True

#check that we obtain the same message after converting to bytes and converting back from bytes
def check_identity(*message_arguments):
    message_a = NetworkMessage(*message_arguments)
    message_b = NetworkMessage()
    message_b.from_bytes( message_a.to_bytes() )
    if check_message_equality(message_a, message_b):
        print("Test... OK")
    
#perform unit tests if the module was not imported
#TODO : more unit tests, especially for exception handling of "bad" messages
if __name__ == '__main__':
    #Test that we obtain the same message after converting to bytes and converting back from bytes
    check_identity("/user/user1/userpage", "ADD", "A new message from user1")
    check_identity("/user/user1/userpage", "ADD", "A new message from user1")
    check_identity("", "ADD", "A new message from user1")
    check_identity("/user/user1/userpage", "", "A new message from user1")
    check_identity("/user/user1/userpage", "ADD", "")
    check_identity("", "", "")
    check_identity("b", "c", "d")
    check_identity("\n", "\n", "\n")
