from network_interface import *

from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import Screen, NoTransition
from kivy.properties import StringProperty
from kivy.lang import Builder

from widgets.scrollable_label import ScrollableLabel
from widgets.shift_enter_textinput import ShiftEnterTextInput

Builder.load_string('''
<ChatClient>:
    BoxLayout:
        orientation: "vertical"
        size: root.size
        
        ScrollableLabel:
            id:label
            text: ""
        ShiftEnterTextInput:
            id:textbox
            size_hint_y: .1
''')
    
class ChatClient(Screen):
    
    #kivy string property indicating the network address of the chat
    chat_address = StringProperty()
    
    #called by Kivy when the screen is entered (displayed)
    def on_enter(self):
        #self.ids["textbox"].font_name=utf8_font_path
        self.ids["textbox"].focus = True
        self.ids["textbox"].text_validate_unfocus = False
        self.ids["textbox"].bind(on_text_validate=self.send_message)
        self.ids["textbox"].bind(on_key_pressed=self.key_pressed_event)
        
        #indicates if the user is typing or not
        self.isTyping = False
        
        #current typing status of all clients
        self.current_typing_msg = ""
        
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message, connection_made_callback = self.connection_made)
    
    def connection_made(self):
        #connection is established, connect to the target address
        message = Network_Message("dummy_user", self.chat_address, "ENTER", "")
        self.network_interface.network_send(message)
    
    def send_message(self, *args):
        msg = self.ids["textbox"].text
        
        if msg and self.network_interface:
            self.isTyping = False
            message = Network_Message("dummy_user", self.chat_address, "APPEND", msg)
            self.network_interface.network_send(message)
            self.ids["textbox"].text = ""
    
    def receive_message(self, message):
        if message.network_command == "IS_TYPING":
            self.add_typing_message(message.message_content)
            return
        
        if message.network_command == "NOTIFICATION":
            #red for notifications
            text_color_str = "ff0000"
        else:
            #black for message content
            text_color_str = "000000"
        
        self.print_message("[color=" + text_color_str + "]" + message.message_content + "\n[/color]")
    
    def print_message(self, msg):
        self.remove_typing_message()
        formatted_links_msg = self.ids["label"].format_links(msg)
        self.ids["label"].text += formatted_links_msg
    
    #============= typing status ===========================
    #typing status is done by storing the current state of typing status
    #when the status changes, we remove the current status from the label, and display the new one (if any)
    def add_typing_message(self, msg):
        text_color_str = "0000ff"
        new_typing_msg = "[color=" + text_color_str + "]    " + msg + " typing... [/color]\n"
        self.current_typing_msg += new_typing_msg
        self.ids["label"].text += new_typing_msg
    
    def remove_typing_message(self):
        status_len = len(self.current_typing_msg)
        if status_len > 0:
            #remove the status_len last characters of the label
            self.ids["label"].text = self.ids["label"].text[:-status_len]
            self.current_typing_msg = ""
    
    #called when a key is pressed in the input
    def key_pressed_event(self, *args):
        #if the user was not already typing, send a TYPING message to the server
        if not self.isTyping:
            self.isTyping = True
            message = Network_Message("dummy_user", self.chat_address, "IS_TYPING", "")
            self.network_interface.network_send(message)
