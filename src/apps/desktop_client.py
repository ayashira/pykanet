
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.lang import Builder

from kivy.properties import BooleanProperty

from apps.login_client import LoginClient
from apps.chat_client import ChatClient
from apps.wiki_client import WikiClient
from apps.turnbasedgame_client import TurnBasedGameClient

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
        
        Button:
            text: "Wiki"
            on_release:
                root.manager.current = "wikiscreen"
        
        Button:
            text: "Tic Tac Toe !"
            on_release:
                root.manager.current = "tictactoescreen"
        
        Button:
            text: "Connect Four"
            on_release:
                root.manager.current = "connectfourscreen"
                
        Button:
            text: "Reversi"
            on_release:
                root.manager.current = "reversiscreen"
''')

class StartScreen(Screen):
    pass


#currently, we close manually the connection of network_interface when a screen is left
#this design is not good. Should be improved later.
    
Builder.load_string('''
<DesktopClient>:
    BoxLayout:
        orientation: "vertical"
        size: root.size
        
        BoxLayout:
            orientation: "horizontal"
            size_hint_y: .1
            
            Button:
                id: home_button
                text: "Home"
                size_hint_x: .3
                disabled: not root.is_logged
                on_release:
                    screen_manager.current = "startscreen"
            Label:
                id: nothing_label
            
        ScreenManager:
            id: screen_manager
            
            LoginClient:
                name: "loginscreen"
                manager: screen_manager
                on_login_finished:
                    self.manager.current = "startscreen"
                    root.is_logged = True
            
            StartScreen:
                name: "startscreen"
                manager: screen_manager

            ChatClient:
                name: "devchatscreen"
                manager: screen_manager
                chat_address: "/chat/dev_main"
                on_leave:
                    self.network_interface.lose_connection()

            ChatClient:
                name: "testchatscreen"
                manager: screen_manager
                chat_address: "/chat/dev_test"
                on_leave:
                    self.network_interface.lose_connection()

            WikiClient:
                name: "wikiscreen"
                manager: screen_manager
                target_address: "/wiki/home"
                on_leave:
                    self.network_interface.lose_connection()
                    self.target_address = "/wiki/home"
            
            TurnBasedGameClient:
                name: "tictactoescreen"
                manager: screen_manager
                target_address: "/game/tic_tac_toe"
                on_leave:
                    self.network_interface.lose_connection()

            TurnBasedGameClient:
                name: "connectfourscreen"
                manager: screen_manager
                target_address: "/game/connect_four"
                on_leave:
                    self.network_interface.lose_connection()

            TurnBasedGameClient:
                name: "reversiscreen"
                manager: screen_manager
                target_address: "/game/reversi"
                on_leave:
                    self.network_interface.lose_connection()
''')

class DesktopClient(Screen):
    
    is_logged = BooleanProperty(False)
