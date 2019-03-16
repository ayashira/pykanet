#Serialize/deserialize python data structures with security checks
#pickle library cannot be used because there is no way to ensure security during deserialization

#Each data block is converted to bytes, and prefixed with the data type and byte length
#Supported types : str, int, bool, list, tuple, dict

#During deserialization, data structure and data range will be checked for security 
#If something goes wrong, None value is returned by deserialization

#Everything here will be critical for safe data exchange 

class BufferTooShortException(Exception): pass
class BufferTooLongException(Exception): pass
class UnknownTypeException(Exception): pass
class BooleanConversionException(Exception): pass
class WrongVersionException(Exception): pass

class Serialize():
    #version number of serialization
    SERIAL_VERSION = 0
    
    #version encoding size
    VERSION_LENGTH = 1
    
    #total serialization length encoded on 4 bytes
    LENGTH_SIZE = 4
    
    #data type described with 1 byte
    TYPE_PREFIX_LENGTH = 1
    
    #maximum length of any data block is 256^4
    #i.e maximum length of a string, a list, or number of elements in a dictionary
    #this is a bit verbose, could be improved to use only 1 byte up to a length of 254
    #  and 255 as an escape character to encode a longer length
    SIZE_PREFIX_LENGTH = 4
    
    DATA_STR_TYPE = 0
    DATA_INT_TYPE = 1
    DATA_BOOL_TYPE = 2
    DATA_LIST_TYPE = 3
    DATA_TUPLE_TYPE = 4
    DATA_DICT_TYPE = 5
    
    #dictionary of supported types
    types_list = {"<class 'str'>":DATA_STR_TYPE, "<class 'int'>":DATA_INT_TYPE, "<class 'bool'>":DATA_BOOL_TYPE,
                  "<class 'list'>":DATA_LIST_TYPE, "<class 'tuple'>":DATA_TUPLE_TYPE, "<class 'dict'>":DATA_DICT_TYPE
    }
    
    def new_buffer():
        complete_message = bytearray(b'')
    
    #convert some value to bytes and add it to some data buffer
    def write_value(buffer, val):        
        #recursive types
        if type(val) is list or type(val) is tuple:
            #encode first the length of the list, and then each value separately
            buffer += Serialize.types_list[str(type(val))].to_bytes(Serialize.TYPE_PREFIX_LENGTH, byteorder='big')
            buffer += (len(val)).to_bytes(Serialize.SIZE_PREFIX_LENGTH, byteorder='big')
            for elmt in val:
                Serialize.write_value(buffer, elmt)
            return
        elif type(val) is dict:
            #encode first the length of the dict, then each (key, value) pair
            buffer += Serialize.types_list[str(type(val))].to_bytes(Serialize.TYPE_PREFIX_LENGTH, byteorder='big')
            buffer += (len(val)).to_bytes(Serialize.SIZE_PREFIX_LENGTH, byteorder='big')
            for key in val.keys():
                Serialize.write_value(buffer, key)
                Serialize.write_value(buffer, val[key])
            return
        
        #basic types
        if type(val) is str:
            value_bytes = val.encode('utf-8')
            buffer += Serialize.types_list[str(type(val))].to_bytes(Serialize.TYPE_PREFIX_LENGTH, byteorder='big')
        elif type(val) is int:
            #use one more byte than the length obtained with bit_length because of using signed numbers
            value_bytes = val.to_bytes(1+( (val.bit_length() + 7) // 8), byteorder='big', signed=True)
            buffer += Serialize.types_list[str(type(val))].to_bytes(Serialize.TYPE_PREFIX_LENGTH, byteorder='big')
        elif type(val) is bool:
            value_bytes = bytearray(b'1') if val else bytearray(b'0')
            buffer += Serialize.types_list[str(type(val))].to_bytes(Serialize.TYPE_PREFIX_LENGTH, byteorder='big')
        buffer += (len(value_bytes)).to_bytes(Serialize.SIZE_PREFIX_LENGTH, byteorder='big')
        buffer += value_bytes
    
    def read_value(buffer, start_idx):
        if len(buffer) < start_idx+Serialize.TYPE_PREFIX_LENGTH:
            raise BufferTooShortException
        data_type = int.from_bytes(buffer[start_idx:start_idx+Serialize.TYPE_PREFIX_LENGTH], byteorder='big')
        start_idx += Serialize.TYPE_PREFIX_LENGTH

        if len(buffer) < start_idx+Serialize.SIZE_PREFIX_LENGTH:
            raise BufferTooShortException
        data_length = int.from_bytes(buffer[start_idx:start_idx+Serialize.SIZE_PREFIX_LENGTH], byteorder='big')
        start_idx += Serialize.SIZE_PREFIX_LENGTH
        
        #recursive types
        if data_type == Serialize.DATA_LIST_TYPE or data_type == Serialize.DATA_TUPLE_TYPE:
            #read each element and append them to the list
            result_list = []
            for _ in range(data_length):
                elmt, start_idx = Serialize.read_value(buffer, start_idx)
                result_list.append(elmt)
            if data_type == Serialize.DATA_LIST_TYPE:
                return result_list, start_idx
            else:
                return tuple(result_list), start_idx
        elif data_type == Serialize.DATA_DICT_TYPE:
            #read each (key, value) pair and add them to the dictionary
            result_dict = {}
            for _ in range(data_length):
                key, start_idx = Serialize.read_value(buffer, start_idx)
                value, start_idx = Serialize.read_value(buffer, start_idx)
                result_dict[key] = value
            return result_dict, start_idx
        
        #basic types
        if len(buffer) < start_idx+data_length:
            raise BufferTooShortException
        
        if data_type == Serialize.DATA_STR_TYPE:
            val = buffer[start_idx:start_idx+data_length].decode('utf-8')
        elif data_type == Serialize.DATA_INT_TYPE:
            val = int.from_bytes(buffer[start_idx:start_idx+data_length], byteorder='big', signed=True)
        elif data_type == Serialize.DATA_BOOL_TYPE:
            if data_length != 1:
                raise BooleanConversionException
            val = True if buffer[start_idx:start_idx+data_length] == bytearray(b'1') else False
        else:
            raise UnknownTypeException
        
        start_idx += data_length
        return val, start_idx
    
    def to_bytes_unguarded(val):
        buffer = bytearray(b'')
        
        #reserve the space for encoding the total length
        buffer += int(0).to_bytes(Serialize.LENGTH_SIZE, byteorder='big')        
        
        #serialization encoding version
        buffer += int(Serialize.SERIAL_VERSION).to_bytes(Serialize.VERSION_LENGTH, byteorder='big')
        
        #serialize data
        Serialize.write_value(buffer, val)
        
        #initialize the total length in front of serialization with real value
        buffer[:Serialize.LENGTH_SIZE] = (len(buffer)).to_bytes(Serialize.LENGTH_SIZE, byteorder='big')
        
        return buffer
        
    def from_bytes_unguarded(bytes_array):
        #read the total length
        if len(bytes_array) < Serialize.LENGTH_SIZE:
            raise BufferTooShortException
        total_length = int.from_bytes(bytes_array[0:Serialize.LENGTH_SIZE], byteorder='big')
        start_idx = Serialize.LENGTH_SIZE
        
        if len(bytes_array) < total_length:
            raise BufferTooShortException
        
        #read the serialization encoding version
        if len(bytes_array) < start_idx + Serialize.VERSION_LENGTH:
            raise BufferTooShortException
        version = int.from_bytes(bytes_array[start_idx:start_idx+Serialize.VERSION_LENGTH], byteorder='big')
        if version != Serialize.SERIAL_VERSION:
            #print("wrong version")
            raise WrongVersionException 
        start_idx += Serialize.VERSION_LENGTH
        
        #deserialize data
        val, start_idx = Serialize.read_value(bytes_array, start_idx)
        
        if start_idx < len(bytes_array):
            #some data in the buffer was not used, we also consider this as an anormal case
            raise BufferTooLongException
        
        return val
    
    #only difference with unguarded is that all exceptions are catched, and None is returned    
    def to_bytes(val):
        try:
            return Serialize.to_bytes_unguarded(val)
        except:
            return None
    
    #only difference with unguarded is that all exceptions are catched and None is returned
    def from_bytes(bytes_array):
        try:
            return Serialize.from_bytes_unguarded(bytes_array)
        except:
            return None

def test_identity(value):
    new_value = Serialize.from_bytes( Serialize.to_bytes(value) )
    if new_value != value:
        print("Identity FAILED", value, new_value)

if __name__ == '__main__':
    #======= Test that deserialization(serialization()) = Identity ========
    
    #strings
    test_identity("")
    test_identity("a")
    test_identity("abcdefghij")
    test_identity("test\n\n\t\\\\test")
    
    #numbers
    test_identity(0)
    test_identity(123450)
    test_identity(11111111111112222222222222233333333333333)
    
    #negative numbers
    test_identity(-21)
    test_identity(-24563)
    test_identity(-2111111111111111111111112222222222222222)
    
    #random numbers
    import random
    for _ in range(10000):
        x = random.randint(0, 100000000000000000000)
        test_identity(x)
        test_identity(-x)
    
    #booleans
    test_identity(True)
    test_identity(False)
    
    #list of same elements
    test_identity([])
    test_identity([""])
    test_identity(["aaaa"])
    test_identity(["aaaa", "bbbb"])
    test_identity(["abc", "defghy", "", "ertetrer", "a", "", "dfg", "df", "df"])
    test_identity([12, 345, -543525])
    test_identity([121212121, -121212345, 12543525, 0, 0, 1, -12121, 3244])
    test_identity([True, False, True, True, True, True, False])
    
    #mixed list
    test_identity(["abc", 123, 32444444444444444444444444, True, True, 344])
    
    #list of list
    test_identity([ [12, 12], [123, 234, 345], [0, 1, 2, 3, 4] ])
    test_identity([[]])
    test_identity([ [], [1], [2, 3], [4, 5, 6], [], [], ["abc", "def"] ])
    
    #multiple levels of list
    test_identity([ [1, 2, [3, 4, [2], [ [34, ""], "aa" ]], [[[[[[1, 2], [[[]]] ]]]]]  ], [[[], 3], 4], 5 ])
    test_identity([[[[[[[[[[[[[[[[[[[[[[[[[1, 2], 3], True], False, False], []], 1]]]], 1]]], 3]], 4]]]]]]]]]]])
    
    #tuples
    test_identity( (0,) )
    test_identity( (1, 2, 3) )
    test_identity( ([1, 2], [-2, 5], 3) )
    test_identity( [(1,2), (59, 34)] )
    
    #dictionaries
    test_identity({})
    test_identity({1:"test1", 2:"test2", 3:"test3"})
    test_identity({1112:123, 25435:2343243, 3242343:565464})
    test_identity({"aaa":True, "b":False, "ccc":True, "ddd":True})
    
    #complex dictionaries
    test_identity({"aa":[True, "test"], "b":"rewtrrr", "c":[[["re"], "rr"]], "ddd":23})
    test_identity({24: [-3, 4, 5], "aa":[4, 5, (-6, 6), (-7, -8), {34:56, 78:79} ]})
    
    #horrible structure
    test_identity([[[[  ], {1:(2,(2,((2,), (2,(2,[[[]]]))))), 3:[[{"a":[[[{1:{1:{1:[[[{}]]]}}}]]]}]]} ], [[True, 12, "a", [], {}, {1:{}}]] ], {-2:{-1:{-2:{-3:[]}}}} ])
    
    #======== Test faulty length ====================
    #serialize, delete one character, serialize, and check that result is None
    s = Serialize.to_bytes(["1", "2", "3"])
    for i in range(2, len(s)):
        t = s[:i] + s[i+1:]
        if Serialize.from_bytes(t) != None:
            print("FAIL. Faulty array could be deserialized", i, Serialize.from_bytes(t))
            print(s)
            print(t)

    #test of array without at least 4 bytes of total length in front 
    s = Serialize.to_bytes(["1", "2", "3"])
    for i in range(4):
        t = s[:i]
        try:
            a = Serialize.from_bytes_unguarded(t)
        except BufferTooShortException:
            #in this test, this is the normal case
            pass
        else:
            print("FAIL. BufferTooShortException was not raised.")
    
    #test of array shorter than indicated by the total length in front 
    s = Serialize.to_bytes({1:"aaa", 2:"bbb", 3:"ccccccc"})
    for i in range(4, len(s)):
        t = s[:i]
        try:
            a = Serialize.from_bytes_unguarded(t)
        except BufferTooShortException:
            #in this test, this is the normal case
            pass
        else:
            print("FAIL. BufferTooShortException was not raised.")
    
    #add a character at the end
    s = Serialize.to_bytes(["1", "2", "3"])
    t = s + bytearray(b'1')
    try:
        a = Serialize.from_bytes_unguarded(t)
    except BufferTooLongException:
        #in this test, this is the normal case
        pass
    else:
        print("FAIL. BufferTooLongException was not raised.")
    
    #test of unknown type
    s = Serialize.to_bytes("1")
    s[Serialize.LENGTH_SIZE + Serialize.VERSION_LENGTH] = 9
    try:
        a = Serialize.from_bytes_unguarded(s)
    except UnknownTypeException:
        #in this test, this is the normal case
        pass
    else:
        print("FAIL. UnknownTypeException was not raised.")
    
    #wrong serial version
    s = Serialize.to_bytes("1")
    s[Serialize.LENGTH_SIZE] = Serialize.SERIAL_VERSION + 5
    try:
        a = Serialize.from_bytes_unguarded(s)
    except WrongVersionException:
        #in this test, this is the normal case
        pass
    else:
        print("FAIL. WrongVersionException was not raised.")
    
    #TODO: test of using wrongly more than 1 byte for a boolean encoding
