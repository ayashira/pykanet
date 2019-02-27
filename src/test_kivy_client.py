# this is a first test of kivy client
# from kivy example : https://github.com/kivy/kivy/blob/master/examples/frameworks/twisted/echo_client_app.py

from __future__ import unicode_literals

import sys
import argparse
import os

#function to parse command line arguments
def parse_arguments():
    #--use_localhost can be used to force the connection to localhost instead of the real distant server
    #this is useful mainly for tests
    parser = argparse.ArgumentParser()
    parser.add_argument('-lh', '--use_localhost', action='store_true')
    parser.add_argument('-og', '--opengl_config', action='store_true')
    
    #parse only the known arguments, and leave the others for kivy parser
    args, unknown = parser.parse_known_args()
    sys.argv[1:] = unknown
    
    return args

#this is not a good practice to parse arguments here instead of __main__
#this is a workaround to strange kivy design that parses arguments directly and silently inside import
custom_args = parse_arguments()

#if opengl_custom, the following flags can be customized here
#maybe it helps to launch Kivy on some old machines (not sure)
if custom_args.opengl_config:
    print("Using customized environment flags")
    os.environ['KIVY_GLES_LIMITS'] = '1'
    os.environ['USE_OPENGL_MOCK'] = '0'
    os.environ['USE_OPENGL_ES2'] = '0'
    os.environ['USE_SDL2'] = '0'

from kivy.support import install_twisted_reactor

install_twisted_reactor()

from network_interface import *

from kivy.app import App
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import ObjectProperty, NumericProperty
from kivy.lang import Builder

from scrollable_label import ScrollableLabel

#Kivy does not include fonts supporting japanese
#A font file must be provided manually
#NOTO font downloaded from here: https://www.google.com/get/noto/help/cjk/
utf8_font_path = "NotoSansCJK-Regular.ttc"


Builder.load_string('''
<ScreenOne>:

    BoxLayout:
        orientation: "vertical"
        size: root.size
        spacing: 20
        padding: 20

        Label:
            text: "Main Menu"
        Button:
            text: "Chat"
            on_release:
                root.manager.current = "screen2"

<ScreenTwo>:
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

<Manager>:
    id: screen_manager

    ScreenOne:
        id: screen_one
        name: "screen1"
        manager: screen_manager

    ScreenTwo:
        id: screen_two
        name: "screen2"
        manager: screen_manager
''')

class ScreenOne(Screen):
    pass
    
class ScreenTwo(Screen):
    connection = None
    network_interface = None
    
    #called by Kivy when the screen is entered (displayed)
    def on_enter(self):
        self.ids["textbox"].font_name=utf8_font_path
        self.ids["textbox"].focus = True
        self.ids["textbox"].text_validate_unfocus = False
        self.ids["textbox"].bind(on_text_validate=self.send_message)
        print("Entered")
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

class Manager(ScreenManager):
    pass


# Main App with a screen manager
class NetworkClientApp(App):

    def build(self):
        m = Manager(transition=NoTransition())
        return m

if __name__ == '__main__':
    #note: command-line arguments are parsed at top of the file, before kivy import
    if custom_args.use_localhost:
        NetworkInterface.set_server_to_localhost()
    
    NetworkClientApp().run()
