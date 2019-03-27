
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from kivy.properties import ObjectProperty

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
        
''')

class LoginClient(Screen):
    '''
        Login screen
        When login is finished, 'on_login_finished' custom event is triggered 
    '''
    
    # login addresses are of the form "/login/username"
    login_address = "/login/"
    
    def __init__(self, **kwargs):
        self.register_event_type('on_login_finished')
        super().__init__(**kwargs)
        
        self.is_register = False
        
        self.network_interface = NetworkInterface(client = self)
    
    def init_inputs(self):
        self.ids["username_input"].text = ""
        self.ids["password_input"].text = ""
        self.ids["username_input"].disabled = False
        self.ids["password_input"].disabled = True
        self.ids["username_input"].focus = True        
    
    def login_start(self):
        self.ids["login_button"].disabled = True
        self.ids["register_button"].disabled = False
        self.init_inputs()
        self.is_register = False
        
    def register_start(self):
        self.ids["login_button"].disabled = False
        self.ids["register_button"].disabled = True
        self.init_inputs()
        self.is_register = True
    
    def username_validated(self):
        self.username = self.ids["username_input"].text
        self.ids["password_input"].disabled = False
        self.ids["password_input"].focus = True        

    def password_validated(self):
        self.password = self.ids["password_input"].text
        
        if self.is_register:
            #TODO            
            pass
        else:
            # TODO: check that the username and password are valid
            
            # set the username for network messages
            MainUser.set_user(self.username)
        
            # signal that user logging is finished
            self.dispatch('on_login_finished')
    
    def on_login_finished(self):
        pass
