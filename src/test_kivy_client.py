# this is a first test of kivy client
# from kivy example : https://github.com/kivy/kivy/blob/master/examples/frameworks/twisted/echo_client_app.py

from __future__ import unicode_literals

from kivy.support import install_twisted_reactor

install_twisted_reactor()

from network_interface import *

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

#Kivy does not include fonts supporting japanese
#A font file must be provided manually
#NOTO font downloaded from here: https://www.google.com/get/noto/help/cjk/
utf8_font_path = "NotoSansCJK-Regular.ttc"

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
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message)
        return root

    def setup_gui(self):
        self.textbox = TextInput(size_hint_y=.1, multiline=False, font_name=utf8_font_path)
        self.textbox.text_validate_unfocus = False
        self.textbox.bind(on_text_validate=self.send_message)
        self.bind(on_start=self.guistart_custom_init)
        self.label = Label(text='', font_name=utf8_font_path)
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
    NetworkClientApp().run()
