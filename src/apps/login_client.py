
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from kivy.properties import ObjectProperty, BooleanProperty

from widgets.custom_labels import FitTextLabel
from widgets.custom_textinputs import VFitTextInput

from user_utils import MainUser
from network_interface import NetworkInterface

Builder.load_string('''
<LoginClient>:
    username_widget: username_input
    BoxLayout:
        orientation: "vertical"
        size: root.size
        spacing: 20
        padding: 20
        
        BoxLayout:
            orientation: "horizontal"
            size_hint_y : .2
            Button:
                id: login_button
                text: "Login"
                disabled: True
                on_release:
                    root.login_start()
            Button:
                id: register_button
                text: "Register"
                on_release:
                    root.register_start()
        
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: .3
            Label:
                text: "Username"
                size_hint_y: None
                height: self.texture_size[1]
            VFitTextInput:
                id:username_input
                multiline: False
                focus: True
                on_text_validate:
                    root.username_validated()
        
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: .3
            Label:
                text: "Password"
                size_hint_y: None
                height: self.texture_size[1]
            VFitTextInput:
                id: password_input
                multiline: False
                password: True
                disabled: True
                on_text_validate: root.password_validated()
        
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: .2
            Label:
                text: "Confirm Password"
                size_hint_y: None
                height: self.texture_size[1]
                opacity: 1 if root.is_register else 0
            VFitTextInput:
                id: confirm_input
                multiline: False
                password: True
                disabled: True
                opacity: 1 if root.is_register else 0
                on_text_validate: root.password_confirmed()
        
        FitTextLabel:
            id: status_label
            text: ""
            size_hint_y: .2
            pos_hint: {'center_x': 0.5}
        
        BoxLayout:
        
''')

class LoginClient(Screen):
    '''
        Login screen
        When login is finished, 'on_login_finished' custom event is triggered.
    '''
    
    is_register = BooleanProperty(False)
    
    # login addresses are of the form "/login/username"
    login_root_address = "/login/"
    
    def __init__(self, **kwargs):
        self.register_event_type('on_login_finished')
        super().__init__(**kwargs)
        
        self.is_register = False
        
        self.network_interface = NetworkInterface(client = self)
    
    def init_inputs(self):
        self.ids["username_input"].text = ""
        self.ids["password_input"].text = ""
        self.ids["confirm_input"].text = ""
        self.ids["username_input"].disabled = False
        self.ids["password_input"].disabled = True
        self.ids["confirm_input"].disabled = True
        self.ids["username_input"].focus = True        
    
    def login_start(self):
        self.ids["login_button"].disabled = True
        self.ids["register_button"].disabled = False
        self.ids["status_label"].text = ""
        self.init_inputs()
        self.is_register = False
        
    def register_start(self):
        self.ids["login_button"].disabled = False
        self.ids["register_button"].disabled = True
        self.ids["status_label"].text = ""
        self.init_inputs()
        self.is_register = True
    
    def username_validated(self):
        if self.is_register:
            if len(self.ids["username_input"].text) < 4:
                self.ids["status_label"].text = "Username: 4 characters needed."
                return
            if not self.ids["username_input"].text.isalnum():
                self.ids["status_label"].text = "Username: letters and numbers only."
                return
        
        self.username = self.ids["username_input"].text
        self.ids["status_label"].text = ""
        self.ids["password_input"].disabled = False
        self.ids["password_input"].focus = True
    
    def password_validated(self):
        self.password = self.ids["password_input"].text
        
        if self.is_register:
            if len(self.ids["password_input"].text) < 8:
                self.ids["status_label"].text = "Password: 8 characters needed."
                return
            
            self.ids["status_label"].text = ""
            self.ids["confirm_input"].disabled = False
            self.ids["confirm_input"].focus = True
        else:
            self.start_network_login()
    
    def password_confirmed(self):
        if not self.is_register:
            return
        
        #check that the confirmed password is the same as the password
        if self.ids["confirm_input"].text != self.password:
            self.ids["status_label"].text = "Passwords are different."
            self.ids["password_input"].text = ""
            self.ids["password_input"].disabled = False
            self.ids["password_input"].focus = True
            self.ids["confirm_input"].text = ""
            self.ids["confirm_input"].disabled = True
            return
        
        self.ids["status_label"].text = ""
        
        # create a pair of private/public keys
        MainUser.create_keys()
        
        # Export the keys to a binary format.
        # Private key is encrypted with user password.
        user_public_key = MainUser.export_public_key()
        user_private_key = MainUser.export_private_key(self.password)
        
        # ask the server to create the new user
        user_address = LoginClient.login_root_address + self.username
        self.network_interface.send(user_address, "CREATE", [self.username, user_public_key, user_private_key])

    def start_network_login(self):
        # read user login data
        # Password check is done on client side, when trying to decrypt the private key
        # received from the server.
        user_address = LoginClient.login_root_address + self.username
        self.network_interface.send(user_address, "READ_USER_LOGIN_DATA", "")
        
    def receive_message(self, message):
        if message.command == "USER_ALREADY_EXISTS":
            self.ids["status_label"].text = "User already exists"
            self.ids["password_input"].text = ""
            self.ids["confirm_input"].text = ""
            self.ids["username_input"].disabled = False
            self.ids["password_input"].disabled = True
            self.ids["confirm_input"].disabled = True
            self.ids["username_input"].focus = True        
            self.ids["username_input"].focus = True
        elif message.command == "USER_NOT_EXISTING":
            self.ids["status_label"].text = "User not existing"
            self.ids["password_input"].text = ""
            self.ids["password_input"].disabled = True
            self.ids["username_input"].focus = True
        elif message.command == "USER_CREATED":
            username = message.content
            popup = Popup(title='User creation',
              content=Label(text='User ' + username + ' created!'),
              size_hint=(None, None), size=(200, 200))
            popup.bind(on_dismiss=self.user_creation_finished)
            popup.open()
        elif message.command == "USER_LOGIN_DATA":
            username, creation_time, public_key, private_key = message.content
            MainUser.set_user(username)
            MainUser.import_public_key(public_key)
            
            # try to decrypt the private key with the given password
            try:
                MainUser.import_private_key(private_key, self.password)
            except:
                # incorrect password
                self.ids["status_label"].text = "Incorrect password"
                self.ids["password_input"].text = ""
                self.ids["password_input"].focus = True
                return
            
            # signal that user logging is finished
            self.dispatch('on_login_finished')

    # called when successful user creation popup is closed 
    def user_creation_finished(self, instance):
        # start the login process with the newly created username/password
        self.start_network_login()
    
    def on_login_finished(self):
        pass
