
import hashlib

#Interface to the host file system
#All "file accesses" should be done through this class
#It will allow in the future to cache data, and also reorganize it and store it efficiently 
class File_Manager():
    def file_read(network_path):
        filename = hashlib.sha224(network_path.encode('utf-8')).hexdigest()
        try:
            with open(filename) as file:
                return file.read()
        except:
            #could not read the file (probably file not existing yet)
            return ""
    
    #TODO: for efficiency, some cache mechanism could be used
    #return True if writing was successful
    def file_write(network_path, new_content):
        filename = hashlib.sha224(network_path.encode('utf-8')).hexdigest()
        try:
            with open(filename, "w") as file:
                file.write(new_content)
            return True
        except:
            print("Warning: could not open file ", filename, "to save data of ", network_path)
            return False
    
    #TODO: for efficiency, some cache mechanism could be used
    def file_append(network_path, added_content):
        filename = hashlib.sha224(network_path.encode('utf-8')).hexdigest()
        try:
            with open(filename, "a") as file:
                file.write(added_content)
        except:
            print("Warning: could not open file ", filename, "to save data of ", network_path)
