from network_interface import NetworkInterface
from network_message import NetworkMessage

from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import Screen, NoTransition
from kivy.properties import StringProperty
from kivy.lang import Builder

from widgets.custom_labels import TitledLabel, FitTextRoundedLabel
from widgets.shift_enter_textinput import ShiftEnterTextInput

from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.properties import StringProperty, ListProperty

from kivy.clock import Clock

from datetime import datetime
from dateutil import tz

from user_utils import MainUser

def convert_utc_to_local(utc_time):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    return local.strftime('%Y-%m-%d, %H:%M:%S')

def convert_utc_to_local_HM(utc_time):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    return local.strftime('%H:%M')
    
Builder.load_string('''
<ChatClient>:
    BoxLayout:
        orientation: "vertical"
        size: root.size
        
        ScrollView:
            scroll_y:0
            BoxLayout:
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                padding: [12, 0, 12, 0]
                spacing: 5
                id:main_view
        ShiftEnterTextInput:
            id:textbox
            size_hint_y: .1
''')

class ChatClient(Screen):
    
    # kivy string property indicating the network address of the chat
    chat_address = StringProperty()
    
    # called by Kivy when the screen is entered (displayed)
    def on_enter(self):
        #self.ids["textbox"].font_name=utf8_font_path
        self.ids["textbox"].focus = True
        self.ids["textbox"].text_validate_unfocus = False
        self.ids["textbox"].bind(on_text_validate=self.send_message)
        self.ids["textbox"].bind(on_key_pressed=self.key_pressed_event)
        
        # remove existing widgets when the screen is entered
        # note : could be improved later
        self.ids["main_view"].clear_widgets()
        self.scroll_y = 0
        
        # indicates if the user is typing or not
        self.isTyping = False
        
        # current typing status of all clients
        self.current_typing_msg = ""
        self.typing_widget = None
        
        self.last_msg_date = None
        
        #current content
        self.content = []
        
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message, connection_made_callback = self.connection_made)
    
    def connection_made(self):
        # connection is established, connect to the target address
        message = NetworkMessage(self.chat_address, "ENTER", "")
        self.network_interface.send(message)
    
    def send_message(self, *args):
        msg = self.ids["textbox"].text
        
        if msg and self.network_interface:
            self.isTyping = False
            message = NetworkMessage(self.chat_address, "APPEND", msg)
            self.network_interface.send(message)
            self.ids["textbox"].text = ""
    
    def receive_message(self, message):
        if message.command == "IS_TYPING":
            self.add_typing_message(message.content)
            return
        
        #TODO: clean up code below
        if message.command == "INIT_CONTENT":
            self.content = message.content
            self.item_add_last = len(self.content)
            self.init_displayed_content()
        elif message.command == "APPEND":
            item = message.content
            self.content.append(item)
            text_color_str = "000000"
            self.print_message(item[2], text_color_str, msg_time=item[0], username=item[1])
        elif message.command == "NOTIFICATION_NEW_CLIENT":
            item = message.content
            # red for notifications
            text_color_str = "ff0000"
            self.print_message("A new guest is here \^_^/ : " + item[1], text_color_str, msg_time=item[0])
        elif message.command == "NOTIFICATION_CLIENT_LIST":
            # we receive a list [time, username, otheruser1, otheruser2, ...]
            # red for notifications
            text_color_str = "ff0000"
            text = ""
            if len(message.content) > 2:
                text += "Currently connected guests: "
                for item in message.content[2:]:
                    text += item + " "
            else:
                text += "No other guest currently connected."
            text += "\nYou are guest : " + message.content[1]
            self.print_message(text, text_color_str, msg_time=message.content[0])
        elif message.command == "NOTIFICATION_CLIENT_LEFT":
            # red for notifications
            text_color_str = "ff0000"
            self.print_message("Chat left by " + message.content[1], text_color_str, msg_time=message.content[0])
    
    # Init the displayed content
    # For a more reactive initialization, messages are added in small batches of 20 messages
    # It allows Kivy to refresh the screen before all messages are added
    # Batches of messages are added from the end of the messages (so that the last messages are immediately visible)
    # In the future, we could do some more advanced processing with kivy RecycleView
    # dt argument not used here. Set to the delta-time by Kivy.
    def init_displayed_content(self, dt = 0):
        # stop the initialization when all messages have been added
        if self.item_add_last == 0:
            return
        
        self.item_add_start = max(0, self.item_add_last - 20)
        
        # insert all new messages above the existing ones
        insert_idx = len(self.ids["main_view"].children)
        #print("insert idx", insert_idx)
        
        for item in self.content[self.item_add_start:self.item_add_last]:
            text_color_str = "000000"
            self.print_message(item[2], text_color_str, msg_time=item[0], username=item[1], insert_idx = insert_idx)        
        
        self.item_add_last = self.item_add_start
        
        #schedule initialization of the next batch of messages
        Clock.schedule_once(self.init_displayed_content)
        
    def print_message(self, msg, text_color_str, msg_time=None, username=None, isTyping = False, insert_idx=0):
        self.remove_typing_message()
        
        # Insert a label with the date if day of new message is different from last message
        if msg_time != None:
            msg_local_time = convert_utc_to_local(msg_time)
            if self.last_msg_date is None or \
               msg_local_time[:10] != self.last_msg_date[:10]:
                day_label = FitTextRoundedLabel()
                day_label.set_text(msg_local_time[5:10], text_color="000000")
                day_label.bcolor = [0.8,1,0.8,1]
                day_label.pos_hint = {'center_x': 0.5}
                self.ids["main_view"].add_widget(day_label, insert_idx)
            self.last_msg_date = msg_local_time
        
        # main message label
        label = TitledLabel()
        label.set_text(msg, text_color=text_color_str)
        if username == MainUser.username:
            # for message from the user itself, blue background and label on the right
            label.bcolor = [0.8,0.93,1,1]
            label.pos_hint = {'right': 1}
        
        # minor label with time and user name
        if msg_time is not None:
            title_txt = ""
            if username == MainUser.username:
                # don't display username and aligned on right
                label.title_to_right()
            elif username is not None:
                title_txt =  username + "  " 
            title_txt += "[size=12]" + convert_utc_to_local_HM(msg_time) + " [/size]"
            label.set_title_text(title_txt)
        
        self.ids["main_view"].add_widget(label, insert_idx)
        
        if isTyping:
            self.typing_widget = label
    
    #============= typing status ===========================
    # Typing status is done by storing the current state of typing status
    # When the status changes, we remove the current status from the label, and display the new one (if any)
    def add_typing_message(self, msg):
        text_color_str = "0000ff"
        if self.current_typing_msg != "":
            self.current_typing_msg += "\n"
        self.current_typing_msg += msg + " is typing..."
        self.print_message(self.current_typing_msg, text_color_str, isTyping = True)
    
    def remove_typing_message(self):
        if not self.typing_widget is None:
            self.ids["main_view"].remove_widget(self.typing_widget)
            self.typing_widget = None
            self.current_typing_msg = ""
    
    # called when a key is pressed in the input
    def key_pressed_event(self, *args):
        # if the user was not already typing, send a TYPING message to the server
        if not self.isTyping:
            self.isTyping = True
            message = NetworkMessage(self.chat_address, "IS_TYPING", "")
            self.network_interface.send(message)
