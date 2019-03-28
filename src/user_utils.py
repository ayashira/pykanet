'''
    Classes to manage users and user authentification
    
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

from serialization_utils import Serialize

class CryptUtil():
    '''
        Wrapper for Elliptic curve cryptography
        This class uses the "cryptography" python library.
        
        Elliptic curve used:
          SECP256K1
        Public key serialization:
          PEM format https://en.wikipedia.org/wiki/Privacy-Enhanced_Mail
        Private key serialization:
          PEM-PKCS8 format https://en.wikipedia.org/wiki/PKCS_8
    '''
    
    # version number of cryptography utility
    CRYPT_VERSION = 0
    
    def generate_key():
        '''
            Generate a random public/private key
        '''
        
        # default_backend() is in fact the only backend existing in cryptography library
        # see: https://cryptography.io/en/latest/hazmat/backends/
        # so there is no risk of different default_backend() between users
        
        # We can choose here which elliptic curve is used
        # SECP384R1 is somewhat standard (supported in most browsers for example)
        # SECP256K1 is the curve used in Bitcoin network
        
        private_key = ec.generate_private_key(ec.SECP256K1(), default_backend())
        public_key = private_key.public_key()
        return public_key, private_key
    
    def sign_bytes(private_key, byte_data):
        '''
            Sign an array of bytes with a private key
            Return an array of bytes
        '''
        
        signature = private_key.sign(byte_data,ec.ECDSA(hashes.SHA256()))
        return signature
        
    def check_sign_bytes(public_key, byte_data, signature):
        '''
            Check the signature of a raw array of bytes with a public key
        '''
        
        try:
            public_key.verify(signature, byte_data, ec.ECDSA(hashes.SHA256()))
        except:
            # verify raises an exception when the signature is invalid
            return False
        return True
    
    def sign(private_key, data):
        '''
            Sign a python data structure with a private key
            Data is converted to an array of bytes with Serialization
            Return an array of bytes
        '''
        
        # Serialize return a byte array
        # Must be converted to bytes for hashing
        byte_data = bytes(Serialize.to_bytes(data))
        return CryptUtil.sign_bytes(private_key, byte_data)
    
    def check_sign(public_key, data, signature):
        '''
            Check the signature of a python data structure with a public key
            Data is converted to an array of bytes with Serialization
            Return True if the signature is valid
        '''
        byte_data = bytes(Serialize.to_bytes(data))
        return CryptUtil.check_sign_bytes(public_key, byte_data, signature)
    
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
        
        # Note : BestAvailableEncryption not guaranteed to be the same algorithm over time or between users
        # This is not a problem since the chosen algorithm is also encoded in the PEM format
        # It seems best (at least for now) to leave this choice to the library
        serialized_private = private_key.private_bytes(
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
    
    def create_keys():
        MainUser.public_key, MainUser.private_key = CryptUtil.generate_key()
    
    def export_public_key():
        return CryptUtil.serialize_public(MainUser.public_key)
    
    def export_private_key(password):
        return CryptUtil.serialize_private(MainUser.private_key, password)
    
    def import_public_key(serialized_public_key):
        MainUser.public_key = CryptUtil.load_public(serialized_public_key)
    
    def import_private_key(serialized_private_key, password):
        MainUser.private_key = CryptUtil.load_private(serialized_private_key, password)


# unit tests
if __name__ == '__main__':
    loop_nb = 1000
    fail_nb = 0
    for i in range(loop_nb):
        # check signature of random message with random private/public keys
        random_public_key, random_private_key = CryptUtil.generate_key()
        random_message = [random.randint(1,1000000000), str(random.randint(1,1000000000))]
        sign = CryptUtil.sign(random_private_key, random_message)
        if not CryptUtil.check_sign(random_public_key, random_message, sign):
            print("FAIL: Signature could not be checked with correct key.")
            fail_nb += 1
        
        # check again with serialized/deserialized keys
        serialized_public_key = CryptUtil.serialize_public(random_public_key)
        loaded_public_key = CryptUtil.load_public(serialized_public_key)
        serialized_private_key = CryptUtil.serialize_private(random_private_key, "testpassword")
        loaded_private_key = CryptUtil.load_private(serialized_private_key, "testpassword")
        sign = CryptUtil.sign(loaded_private_key, random_message)
        if not CryptUtil.check_sign(loaded_public_key, random_message, sign):
            print("FAIL: Signature could not be checked after serialization of keys.")
            fail_nb += 1
        
        # check that a different public key fails
        random_public_key2, random_private_key2 = CryptUtil.generate_key() 
        sign2 = CryptUtil.sign(random_private_key2, random_message)
        if CryptUtil.check_sign(random_public_key, random_message, sign2):
            print("FAIL: Signature checked with incorrect key")
            fail_nb += 1
    
    print("Signature checks. Total number of fails: ", fail_nb ,"/", loop_nb)
