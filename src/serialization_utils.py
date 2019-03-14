#Serialize/deserialize python data structures with security checks
#pickle library cannot be used because there is no way to ensure security during deserialization

#Each data block is converted to bytes, and prefixed with the data type and byte length

#During deserialization, data structure and data range will be checked for security 

#Everything here will be critical for safe data exchange 

class Serialize():
    TYPE_PREFIX_LENGTH = 1
    SIZE_PREFIX_LENGTH = 3
    
    DATA_STR_TYPE = 0
    DATA_INT_TYPE = 1
    DATA_BOOL_TYPE = 2
    DATA_LIST_TYPE = 3
    DATA_DICT_TYPE = 4
    
    #dictionary of supported types
    types_list = {"<class 'str'>":DATA_STR_TYPE, "<class 'int'>":DATA_INT_TYPE, "<class 'bool'>":DATA_BOOL_TYPE,
                  "<class 'list'>":DATA_LIST_TYPE, "<class 'dict'>":DATA_DICT_TYPE
    }
    
    def new_buffer():
        complete_message = bytearray(b'')
    
    #convert some value to bytes and add it to some data buffer
    def write_value(buffer, val):        
        #recursive types
        if type(val) is list:
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
            value_bytes = val.to_bytes((val.bit_length() + 7) // 8, byteorder='big')
            buffer += Serialize.types_list[str(type(val))].to_bytes(Serialize.TYPE_PREFIX_LENGTH, byteorder='big')
        elif type(val) is bool:
            value_bytes = bytearray(b'1') if val else bytearray(b'0')
            buffer += Serialize.types_list[str(type(val))].to_bytes(Serialize.TYPE_PREFIX_LENGTH, byteorder='big')
        buffer += (len(value_bytes)).to_bytes(Serialize.SIZE_PREFIX_LENGTH, byteorder='big')
        buffer += value_bytes
    
    def read_value(buffer, start_idx):
        data_type = int.from_bytes(buffer[start_idx:start_idx+Serialize.TYPE_PREFIX_LENGTH], byteorder='big')
        start_idx += Serialize.TYPE_PREFIX_LENGTH
        data_length = int.from_bytes(buffer[start_idx:start_idx+Serialize.SIZE_PREFIX_LENGTH], byteorder='big')
        start_idx += Serialize.SIZE_PREFIX_LENGTH
        
        #recursive types
        if data_type == Serialize.DATA_LIST_TYPE:
            #read each element and append them to the list
            result_list = []
            for _ in range(data_length):
                elmt, start_idx = Serialize.read_value(buffer, start_idx)
                result_list.append(elmt)
            return result_list, start_idx
        elif data_type == Serialize.DATA_DICT_TYPE:
            #read each (key, value) pair and add them to the dictionary
            result_dict = {}
            for _ in range(data_length):
                key, start_idx = Serialize.read_value(buffer, start_idx)
                value, start_idx = Serialize.read_value(buffer, start_idx)
                result_dict[key] = value
            return result_dict, start_idx
        
        #basic types
        if data_type == Serialize.DATA_STR_TYPE:
            val = buffer[start_idx:start_idx+data_length].decode('utf-8')
        elif data_type == Serialize.DATA_INT_TYPE:
            val = int.from_bytes(buffer[start_idx:start_idx+data_length], byteorder='big')
        elif data_type == Serialize.DATA_BOOL_TYPE:
            val = True if buffer[start_idx:start_idx+1] == bytearray(b'1') else False
        start_idx += data_length
        return val, start_idx
    
    def to_bytes(val):
        buffer = bytearray(b'')
        Serialize.write_value(buffer, val)
        return buffer
        
    def from_bytes(bytes_array):
        val, _ = Serialize.read_value(bytes_array, 0)
        return val

def test_identity(value):
    new_value = Serialize.from_bytes( Serialize.to_bytes(value) )
    if new_value != value:
        print("Identity FAILED", value, new_value)

if __name__ == '__main__':
    #Test that we obtain the same value after serialization/deserialization
    
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
    #test_identity(-21)
    
    #booleans
    test_identity(True)
    test_identity(False)
    
    #list of same elements
    test_identity([])
    test_identity([""])
    test_identity(["aaaa"])
    test_identity(["aaaa", "bbbb"])
    test_identity(["abc", "defghy", "", "ertetrer", "a", "", "dfg", "df", "df"])
    test_identity([12, 345, 543525])
    test_identity([121212121, 121212345, 12543525, 0, 0, 1, 12121, 3244])
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
    
    #dictionaries
    test_identity({})
    test_identity({1:"test1", 2:"test2", 3:"test3"})
    test_identity({1112:123, 25435:2343243, 3242343:565464})
    test_identity({"aaa":True, "b":False, "ccc":True, "ddd":True})
    
    #complex dictionaries
    test_identity({"aa":[True, "test"], "b":"rewtrrr", "c":[[["re"], "rr"]], "ddd":23})
    test_identity({24: [3, 4, 5], "aa":[4, 5, 6, 7, {34:56, 78:79} ]})
    
    #horrible structure
    test_identity([[[[  ], {1:2, 3:[[{"a":[[[{1:{1:{1:[[[{}]]]}}}]]]}]]} ], [[True, 12, "a", [], {}, {1:{}}]] ], {2:{1:{2:{3:[]}}}} ])
