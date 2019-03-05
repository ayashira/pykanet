from network_interface import *

from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from kivy.properties import StringProperty
from kivy.lang import Builder

#from scrollable_label import ScrollableLabel
#from shift_enter_textinput import ShiftEnterTextInput

from turnbasedgame_list import TurnBasedGame_List

Builder.load_string('''
<TurnBasedGameClient>:
    GridLayout:
        id: board_grid
        size: root.size
''')


class TurnBasedGameClient(Screen):
    
    #kivy string property indicating the target network address
    target_address = StringProperty()
    
    #called by Kivy when the screen is entered (displayed)
    def on_enter(self):
        self.game_board = TurnBasedGame_List.get_game_from_name(self.target_address)
        
        self.create_grid()
        
        #game state
        self.play_turn = False
        
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message, connection_made_callback = self.connection_made)
    
    def create_grid(self):
        rows = self.game_board.rows()
        cols = self.game_board.cols()
        cell_width, cell_height = self.game_board.cell_size()
        
        self.ids["board_grid"].rows = rows
        self.ids["board_grid"].cols = cols
        
        #list of buttons used to access buttons from an index
        self.button_list = []
        
        for i in range(rows):
            for j in range(cols):
                #note : button id defined here cannot be used to access buttons with their .ids
                #       it is used to identify which button called cell_clicked
                button = Button(text='', width=cell_width, height=cell_height, size_hint=(None, None), id=str(i*rows+j))
                button.bind(on_press=self.cell_clicked)
                self.ids["board_grid"].add_widget(button)
                self.button_list.append(button)
    
    def connection_made(self):
        #connection is established, connect to the target address
        message = Network_Message("dummy_user", self.target_address, "ENTER", "")
        self.network_interface.network_send(message)
        
    def receive_message(self, message):
        #print(message.to_bytes())
        if message.network_command == "REQUEST_MOVE":
            self.play_turn = True
        elif message.network_command == "PLAYER1_MOVE":
            move = int(message.message_content)
            self.game_board.play(move, player=1)
            self.button_list[move].text = "O"
        elif message.network_command == "PLAYER2_MOVE":
            move = int(message.message_content)
            self.game_board.play(move, player=2)
            self.button_list[move].text = "X"
        elif message.network_command == "PLAYER1_WIN" or message.network_command == "PLAYER2_WIN" or message.network_command == "DRAW":
            popup = Popup(title='Game finished',
                          content=Label(text=message.network_command),
                          size_hint=(None, None), size=(200, 200))
            popup.open()
    
    def cell_clicked(self, button):
        #print(button.id)
        if self.play_turn:
            move = int(button.id)
            if not self.game_board.is_valid_play(move, player=2):
                return
            
            self.play_turn = False
            message = Network_Message("dummy_user", self.target_address, "MOVE", button.id)
            self.network_interface.network_send(message)
