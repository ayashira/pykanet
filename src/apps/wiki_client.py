from network_interface import NetworkInterface
from network_message import NetworkMessage

from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import Screen, NoTransition
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.properties import BooleanProperty

from widgets.scrollable_label import ScrollableLabel

Builder.load_string('''
<WikiClient>:
    BoxLayout:
        orientation: "vertical"
        size: root.size
        
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: .1
            
            Button:
                id: edit_button
                text: "Edit"
                disabled: root.is_edit
                on_release: 
                    screen_manager.current = "edit_screen"
                    root.is_edit = True
                    root.start_edit()
            
            Button:
                id: cancel_button
                text: "Cancel"
                disabled: not root.is_edit
                on_release:
                    screen_manager.current = "display_screen"
                    root.is_edit = False
                    root.cancel_edit()

            Button:
                id: save_button
                text: "Save"
                disabled: not root.is_edit
                on_release:
                    screen_manager.current = "display_screen"
                    root.is_edit = False
                    root.save_edit()
        
        ScreenManager:
            id: screen_manager
            Screen:
                id: display_screen
                name: "display_screen"
                ScrollableLabel:
                    id:label
                    text: ""
                    on_link_clicked:
                        root.target_address = "/wiki/" + args[1]
                        root.read_address(root.target_address)
            Screen:
                id: edit_screen
                name: "edit_screen"
                TextInput:
                    multiline: True
                    id:textbox
''')

class WikiClient(Screen):
    
    #kivy string property indicating the target network address
    target_address = StringProperty()
    
    is_edit = BooleanProperty(False)
    
    #called by Kivy when the screen is entered (displayed)
    def on_enter(self):
        #self.ids["textbox"].font_name=utf8_font_path
        self.ids["textbox"].text_validate_unfocus = False
        
        self.ids["screen_manager"].transition = NoTransition()
        
        self.current_content = ""
        
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message, connection_made_callback = self.connection_made)
    
    def connection_made(self):
        #connection is established, read the start address
        self.read_address(self.target_address)
    
    def send_message(self, *args):
        msg = self.ids["textbox"].text
        
        if msg and self.network_interface:
            message = NetworkMessage(self.target_address, "WRITE", msg)
            self.network_interface.send(message)
    
    def receive_message(self, message):
        #print(message.command, message.content)
        if message.command == "READ_RESULT":
            self.current_content = message.content
            self.update_text(self.current_content)
        elif message.command == "WRITE_DONE":
            #read the address again after writing
            self.read_address(self.target_address)
    
    def read_address(self, read_target_address):
        message = NetworkMessage(read_target_address, "READ", "")
        self.network_interface.send(message)
    
    def update_text(self, msg):
        formatted_msg = self.ids["label"].format_wiki_syntax(msg)
        
        #black color for main text
        text_color_str = "000000"
        msg_color = "[color=" + text_color_str + "]" + formatted_msg + "[/color]"
        
        self.ids["label"].text = msg_color
    
    def start_edit(self):
        self.ids["textbox"].focus = True
        self.ids["textbox"].text = self.current_content
    
    def save_edit(self):
        msg = self.ids["textbox"].text
        message = NetworkMessage(self.target_address, "WRITE", msg)
        self.network_interface.send(message)
    
        #remove the current content of the label to show that we are waiting the server response
        self.ids["label"].text = ""
    
    def cancel_edit(self):
        #TODO : confirmation popup
        pass
