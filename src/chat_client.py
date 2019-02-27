from network_interface import *

from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import Screen, NoTransition
from kivy.properties import ObjectProperty
from kivy.lang import Builder

from scrollable_label import ScrollableLabel

Builder.load_string('''
<ChatClient>:
    BoxLayout:
        orientation: "vertical"
        size: root.size

        ScrollableLabel:
            id:label
            text: ""
        TextInput:
            id:textbox
            size_hint_y: .1
            multiline: False
''')
    
class ChatClient(Screen):

    #called by Kivy when the screen is entered (displayed)
    def on_enter(self):
        #self.ids["textbox"].font_name=utf8_font_path
        self.ids["textbox"].focus = True
        self.ids["textbox"].text_validate_unfocus = False
        self.ids["textbox"].bind(on_text_validate=self.send_message)
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message, connection_made_callback = self.connection_made)
    
    def connection_made(self):
        #connection is established, connect to the target address
        message = Network_Message("dummy_user", "/chat/dev_main", "ENTER", "")
        self.network_interface.network_send(message)
    
    def send_message(self, *args):
        msg = self.ids["textbox"].text
        
        if msg and self.network_interface:
            message = Network_Message("dummy_user", "/chat/dev_main", "APPEND", msg)
            self.network_interface.network_send(message)
            self.ids["textbox"].text = ""
    
    def receive_message(self, message):
        if message.network_command == "NOTIFICATION":
            #red for notifications
            text_color_str = "ff0000"
        else:
            #black for message content
            text_color_str = "000000"
        
        self.print_message("[color=" + text_color_str + "]" + message.message_content + "[/color]")
    
    def print_message(self, msg):
        self.ids["label"].text += "{}\n".format(msg)
