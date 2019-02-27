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
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.properties import ObjectProperty, NumericProperty
from kivy.lang import Builder

from chat_client import ChatClient

#Kivy does not include fonts supporting japanese
#A font file must be provided manually
#NOTO font downloaded from here: https://www.google.com/get/noto/help/cjk/
utf8_font_path = "NotoSansCJK-Regular.ttc"


Builder.load_string('''
<StartScreen>:

    BoxLayout:
        orientation: "vertical"
        size: root.size
        spacing: 20
        padding: 20

        Label:
            text: "Main Menu. This screen will become the app 'desktop'."
        Button:
            text: "Main Chat"
            on_release:
                root.manager.current = "devchatscreen"
                
        Button:
            text: "Test Chat : do what you want here, this is for tests :)"
            on_release:
                root.manager.current = "testchatscreen"

''')

class StartScreen(Screen):
    pass

    
Builder.load_string('''
<Manager>:
    id: screen_manager

    StartScreen:
        id: screen_one
        name: "startscreen"
        manager: screen_manager

    ChatClient:
        id: screen_two
        name: "devchatscreen"
        manager: screen_manager
        chat_address: "/chat/dev_main"

    ChatClient:
        id: screen_three
        name: "testchatscreen"
        manager: screen_manager
        chat_address: "/chat/dev_test"
''')

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
