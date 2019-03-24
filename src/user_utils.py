'''
    Classes to mnage users and user authentification
    
    User authentification uses Elliptic Curve cryptography.
    cryptography python library needs to be installed.
    Installation with pip: pip install cryptography
'''

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization

# note: used only in the unit tests to generate random strings
import random

class CryptUtil():
    '''
        Wrapper for Elliptic curve cryptography
        This class uses the "cryptography" python library.
    '''
    
    def generate_key():
        '''
            Generate a random public/private key
        '''
        
        # default_backend() is in fact the only backend existing in cryptography library
        # see: https://cryptography.io/en/latest/hazmat/backends/
        # so there is no risk of different default_backend() between users
        private_key = ec.generate_private_key(ec.SECP384R1(), default_backend())
        public_key = private_key.public_key()
        return public_key, private_key
    
    def sign_message(private_key, message):
        '''
            Sign a message with a private key
        '''
        
        data = message.encode('utf-8')
        signature = private_key.sign(data,ec.ECDSA(hashes.SHA256()))
        return signature
        
    def check_sign(public_key, message, signature):
        '''
            Check the signature of a message with a public key
        '''
        
        data = message.encode('utf-8')
        try:
            public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))
        except:
            return False
        return True

    def serialize_public(public_key):
        '''
            Return an ascii-encoded string of the public key in the PEM format
        '''
        
        serialized_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return serialized_public

    def load_public(serialized_public_key):
        '''
            Reconstructs a public key from its serialized encoding
        '''
        
        public_key = serialization.load_pem_public_key(
            serialized_public_key,
            backend=default_backend()
        )
        return public_key
    
    def serialize_private(private_key, password):
        '''
            Return an ascii-encoded string of the private key
            The private key is encrypted with the given password
        '''
        
        # Note : BestAvailableEncryption is not guaranteed to be the same algorithm over time or between users
        # This is not a problem since the chosen algorithm is also encoded in the PEM format
        # It seems best (at least for now) to leave this choice to the library
        serialized_private = random_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(password.encode('utf-8'))
        )
        return serialized_private
    
    def load_private(serialized_private_key, password):
        '''
            Reconstructs a private key from its serialized encoding
            The same password used during serialization is needed.
        '''
        
        private_key = serialization.load_pem_private_key(
            serialized_private_key,
            password=password.encode('utf-8'),
            backend=default_backend()
        )
        return private_key

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
    for i in range(loop_nb):
        random_public_key, random_private_key = CryptUtil.generate_key()
        serialized_public_key = CryptUtil.serialize_public(random_public_key)
        serialized_private_key = CryptUtil.serialize_private(random_private_key, "testpassword")
        
        #if i <= 10:
        #    print(serialized_public_key)
        #    print(serialized_private_key)
        
        random_public_key = CryptUtil.load_public(serialized_public_key)
        random_private_key = CryptUtil.load_private(serialized_private_key, "testpassword")
        
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
