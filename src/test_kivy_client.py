# this is a first test of kivy client
# from kivy example : https://github.com/kivy/kivy/blob/master/examples/frameworks/twisted/echo_client_app.py

from __future__ import unicode_literals

from kivy.support import install_twisted_reactor

install_twisted_reactor()

# A Simple Client that send messages to the Echo Server
from twisted.internet import reactor, protocol

server_port = 8883
server_address = "localhost"

class EchoClient(protocol.Protocol):
    def connectionMade(self):
        self.factory.network_interface.on_connection(self.transport)

    def dataReceived(self, data):
        self.factory.network_interface.dataReceived(data)


class EchoClientFactory(protocol.ClientFactory):
    protocol = EchoClient

    def __init__(self, network_interface):
        self.network_interface = network_interface

    def startedConnecting(self, connector):
        print('Started to connect.')

    def clientConnectionLost(self, connector, reason):
        print('Lost connection.')

    def clientConnectionFailed(self, connector, reason):
        print('Connection failed.')


class NetworkInterface():
    connection = None
    data_received_callback = None
    
    def __init__(self, data_received_callback):
        self.connect_to_server()
        self.data_received_callback = data_received_callback
    
    def network_write(self, data):
        if self.connection:
            self.connection.write(data)
        
    def network_read(self):
        pass

    # =========== private functions ========
    def connect_to_server(self):
        reactor.connectTCP(server_address, server_port, EchoClientFactory(self))
    
    def on_connection(self, connection):
        print("Connected successfully!")
        self.connection = connection

    def dataReceived(self, data):
        self.data_received_callback(data)


from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout


# A simple kivy App, with a textbox to enter messages, and
# a large label to display all the messages received from
# the server
class TwistedClientApp(App):
    connection = None
    textbox = None
    label = None
    network_interface = None

    def build(self):
        root = self.setup_gui()
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message)
        return root

    def setup_gui(self):
        self.textbox = TextInput(size_hint_y=.1, multiline=False)
        self.textbox.text_validate_unfocus = False
        self.textbox.bind(on_text_validate=self.send_message)
        self.bind(on_start=self.guistart_custom_init)
        self.label = Label(text='')
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.label)
        layout.add_widget(self.textbox)
        return layout

    def send_message(self, *args):
        msg = self.textbox.text
        
        if msg and self.network_interface:
            self.network_interface.network_write(msg.encode('utf-8'))
            self.textbox.text = ""
    
    def receive_message(self, data):
        self.print_message(data.decode('utf-8'))
    
    def print_message(self, msg):
        self.label.text += "{}\n".format(msg)

    def guistart_custom_init(self, instance):
        self.textbox.focus = True

if __name__ == '__main__':
    TwistedClientApp().run()