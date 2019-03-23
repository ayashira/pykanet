import hashlib

# note: used only temporarily for dummy implementation
import random

class CryptUtil():
    '''
        Public-key encryption
        For now, this is a dummy class just to provide the interface
        Internal functions will be replaced by calls to a cryptographic library
    '''
    
    # generate a random public/private key
    # for this dummy implementation, public=private
    def generate_key():
        private_key = hashlib.sha256(str(random.randint(1,1000000000)).encode('utf-8')).hexdigest()
        # this is just to have different private/public keys
        public_key = private_key + "xyz"
        return public_key, private_key
    
    # sign a message with a private key
    def sign_message(private_key, message):
        hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
        return hashlib.sha256( (private_key + hash).encode('utf-8')).hexdigest()
    
    # check the signature of a message with a public key
    def check_sign(public_key, message, message_sign):
        hash = hashlib.sha256(message.encode('utf-8')).hexdigest()
        # remove the last 3 characters of the public key in order to obtain the private key
        signature = hashlib.sha256( (public_key[:-3] + hash).encode('utf-8')).hexdigest()
        return signature == message_sign

# singleton-class to manage the main logged user from any part of the program
class MainUser():
    
    username = ""
    user_id = ""
    public_key = ""
    private_key = ""
    
    def set_user(username):
        MainUser.username = username
        
    def set_keys(public_key, private_key):
        MainUser.public_key = public_key
        MainUser.private_key = private_key

# unit tests
if __name__ == '__main__':
    # 1.generate random public, private keys and a random message
    #   generate a second random public, private key
    # 2.sign the random message with the first private key
    #   check that signature is correct with first public key
    # 3.sign that the random message with second private key
    #   check that signature is NOT correct with first public key
    loop_nb = 1000
    fail_nb = 0
    for _ in range(loop_nb):
        random_public_key, random_private_key = CryptUtil.generate_key()
        random_message = str(random.randint(1,1000000000))
        sign = CryptUtil.sign_message(random_private_key, random_message)
        if not CryptUtil.check_sign(random_public_key, random_message, sign):
            print("FAIL: Signature could not be checked with correct key.")
            fail_nb += 1
        
        random_public_key2, random_private_key2 = CryptUtil.generate_key() 
        sign2 = CryptUtil.sign_message(random_private_key2, random_message)
        if CryptUtil.check_sign(random_public_key, random_message, sign2):
            print("FAIL: Signature checked with incorrect key")
            fail_nb += 1
    
    print("Ttoal number of fails: ", fail_nb ,"/", loop_nb)
