from network_interface import *

from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import Screen, NoTransition
from kivy.properties import StringProperty
from kivy.lang import Builder

from widgets.scrollable_label import ScrollableLabel
from widgets.shift_enter_textinput import ShiftEnterTextInput

Builder.load_string('''
<WikiClient>:
    BoxLayout:
        orientation: "vertical"
        size: root.size
        
        Button:
            id: edit_button
            text: "Edit"
            size_hint_y: .1
        
        Button:
            id: edit_button
            text: "Save"
            size_hint_y: .1
        
        ScrollableLabel:
            id:label
            text: ""
        ShiftEnterTextInput:
            id:textbox
            size_hint_y: .5
''')
    
class WikiClient(Screen):
    
    #kivy string property indicating the target network address
    target_address = StringProperty()
    
    #called by Kivy when the screen is entered (displayed)
    def on_enter(self):
        #self.ids["textbox"].font_name=utf8_font_path
        self.ids["textbox"].focus = True
        self.ids["textbox"].text_validate_unfocus = False
        self.ids["textbox"].bind(on_text_validate=self.send_message)
        
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message, connection_made_callback = self.connection_made)
    
    def connection_made(self):
        #connection is established, read the start address
        self.read_address(self.target_address)
    
    def send_message(self, *args):
        msg = self.ids["textbox"].text
        
        if msg and self.network_interface:
            message = Network_Message("dummy_user", self.target_address, "WRITE", msg)
            self.network_interface.network_send(message)
    
    def receive_message(self, message):
        #print(message.network_command, message.message_content)
        if message.network_command == "READ_RESULT":
            self.update_text(message.message_content)
            self.ids["textbox"].text = message.message_content
        elif message.network_command == "WRITE_DONE":
            #read the address again after writing
            self.read_address(self.target_address)
    
    def read_address(self, read_target_address):
        message = Network_Message("dummy_user", read_target_address, "READ", "")
        self.network_interface.network_send(message)
    
    def update_text(self, msg):
        formatted_links_msg = self.ids["label"].format_links(msg)
        
        #black color for main text
        text_color_str = "000000"
        msg_color = "[color=" + text_color_str + "]" + formatted_links_msg + "[/color]"
        
        self.ids["label"].text = msg_color
