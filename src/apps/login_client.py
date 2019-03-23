
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

from kivy.properties import ObjectProperty

from user_utils import MainUser

Builder.load_string('''
<LoginClient>:
    username_widget: username_input
    BoxLayout:
        orientation: "vertical"
        size: root.size
        spacing: 20
        padding: 20
        
        BoxLayout:
        
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: .3
            Label:
                text: "Username"
            TextInput:
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
            TextInput:
                id: password_input
                multiline: False
                password: True
                on_text_validate: root.password_validated()
                
        BoxLayout:
        
''')

class LoginClient(Screen):
    '''
        Login screen
        When login is finished, 'on_login_finished' custom event is triggered 
    '''
    
    def __init__(self, **kwargs):
        self.register_event_type('on_login_finished')
        super().__init__(**kwargs)
    
    def username_validated(self):
        # print(self.ids.keys(), flush=True)
        self.username = self.ids["username_input"].text
        self.ids["password_input"].focus = True

    def password_validated(self):
        self.password = self.ids["password_input"].text
        
        # set the username for network messages
        # TODO: check that the username and password are valid
        MainUser.set_user(self.username)
        
        # signal that user logging is finished
        self.dispatch('on_login_finished')
    
    def on_login_finished(self):
        pass
