
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.lang import Builder

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

    
Builder.load_string('''
<DesktopClient>:
    id: screen_manager

    StartScreen:
        name: "startscreen"
        manager: screen_manager

    ChatClient:
        name: "devchatscreen"
        manager: screen_manager
        chat_address: "/chat/dev_main"

    ChatClient:
        name: "testchatscreen"
        manager: screen_manager
        chat_address: "/chat/dev_test"

    WikiClient:
        name: "wikiscreen"
        manager: screen_manager
        target_address: "/wiki/home"
    
    TurnBasedGameClient:
        name: "tictactoescreen"
        manager: screen_manager
        target_address: "/game/tic_tac_toe"

    TurnBasedGameClient:
        name: "connectfourscreen"
        manager: screen_manager
        target_address: "/game/connect_four"

    TurnBasedGameClient:
        name: "reversiscreen"
        manager: screen_manager
        target_address: "/game/reversi"
''')

class DesktopClient(ScreenManager):
    pass
