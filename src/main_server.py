'''
    Server main file
    Use Twisted library, but not Kivy library
'''

from twisted.internet import reactor
from twisted.internet import protocol

from message_passing_protocol import MessagePassingProtocol
from server_services import ServerServices
from file_manager import FileManager

port_to_listen = 8883

def main():
    # initialize file saving directories
    if not FileManager.init_save_path():
        # file saving not working correctly, we should not run the server
        print("FileManager initialization... [FAILED]. Stopping.")
        return
    else:
        print("FileManager initialization... [OK]")
        
    factory = protocol.ServerFactory()
    factory.protocol = MessagePassingProtocol
    factory.is_server = True
    factory.server_services = ServerServices()
    
    print("Server started...")
    reactor.listenTCP(port_to_listen,factory)
    reactor.run()

if __name__ == '__main__':
    main()
