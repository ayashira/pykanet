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
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder

#Kivy does not include fonts supporting japanese
#A font file must be provided manually
#NOTO font downloaded from here: https://www.google.com/get/noto/help/cjk/
utf8_font_path = "NotoSansCJK-Regular.ttc"

Builder.load_string('''
<ScrollableLabel>:
    scroll_y:0
    Label:
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        text: root.text
        bcolor: 1, 1, 1, 1
        markup:True
        canvas.before:
            Color:
                rgba: self.bcolor
            Rectangle:
                pos: self.pos
                size: self.size
''')

class ScrollableLabel(ScrollView):
    text = StringProperty('')
    bcolor = ListProperty([0,0,0,1])

# A simple kivy App, with a textbox to enter messages, and
# a large label to display all the messages received from
# the server
class NetworkClientApp(App):
    connection = None
    textbox = None
    label = None
    network_interface = None

    def build(self):
        root = self.setup_gui()
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message, connection_made_callback = self.connection_made)
        return root

    def setup_gui(self):
        self.textbox = TextInput(size_hint_y=.1, multiline=False, font_name=utf8_font_path)
        self.textbox.text_validate_unfocus = False
        self.textbox.bind(on_text_validate=self.send_message)
        self.bind(on_start=self.guistart_custom_init)
        self.label = ScrollableLabel(text='', bcolor = [0,0,0,1])
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.label)
        layout.add_widget(self.textbox)
        return layout
    
    def connection_made(self):
        #connection is established, connect to the target address
        message = Network_Message("dummy_user", "/chat/dev_main", "ENTER", "")
        self.network_interface.network_send(message)
    
    def send_message(self, *args):
        msg = self.textbox.text
        
        if msg and self.network_interface:
            message = Network_Message("dummy_user", "/chat/dev_main", "APPEND", msg)
            self.network_interface.network_send(message)
            self.textbox.text = ""
    
    def receive_message(self, message):
        if message.network_command == "NOTIFICATION":
            #red for notifications
            text_color_str = "ff0000"
        else:
            #black for message content
            text_color_str = "000000"
        
        self.print_message("[color=" + text_color_str + "]" + message.message_content + "[/color]")
    
    def print_message(self, msg):
        self.label.text += "{}\n".format(msg)

    def guistart_custom_init(self, instance):
        self.textbox.focus = True

if __name__ == '__main__':
    #note: command-line arguments are parsed at top of the file, before kivy import
    if custom_args.use_localhost:
        NetworkInterface.set_server_to_localhost()
    
    NetworkClientApp().run()
