from user_utils import MainUser
from serialization_utils import Serialize

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
#Most exception handling is done inside Serialize class

class NetworkMessage():
    #constant defining the version number of the message encoding
    MESSAGE_VERSION = 0
    
    #prefix size for the total length
    MESSAGE_PREFIX_SIZE = Serialize.LENGTH_SIZE
    
    #username : utf8 string, username of message sender
    #network_path : utf8 string, target address on the network where the message is sent
    #command : utf8 string, requested action at the target address
    #content : any python data structure supported by Serialize class
    def __init__(self, network_path=None, command=None, content=None):
        self.version = NetworkMessage.MESSAGE_VERSION
        self.username = MainUser.username
        self.network_path = network_path
        self.command = command
        self.content = content
    
    #we convert each subpart of the message to bytes, and prefix each of them with their length in bytes
    #the complete message is also prefixed with the complete message length
    def to_bytes(self):
        return Serialize.to_bytes([self.version, self.username, self.network_path, self.command, self.content])
    
    #read each subpart of the message from a byte encoding
    def from_bytes(self, complete_message):
        result = Serialize.from_bytes(complete_message)
        #None means deserialization did not work correctly
        if result is not None:
            try:
                self.version, self.username, self.network_path, self.command, self.content = result
                
                #ignore messages without the correct version number and correct types
                if self.version != NetworkMessage.MESSAGE_VERSION or type(self.username) is not str \
                  or type(self.network_path) is not str or type(self.command) is not str:
                    self.username = None
                    self.network_path = None
                    self.command = None
                    self.content = None
            except:
                #could not parse the result in the correct list of variables
                pass

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
    
    check_identity("\n", "test", [1, 2, 3, 4])
    check_identity("\n", "\n", [(12,23), (50,20), (40, 20)])
    check_identity("aa", "aaa", {"a":12, "b":[1, 2, 3], "ccc":(-25, {})})
