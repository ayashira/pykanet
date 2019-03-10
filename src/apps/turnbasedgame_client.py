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

from apps.turnbasedgame_list import TurnBasedGameList

Builder.load_string('''
<TurnBasedGameClient>:
    BoxLayout:
        orientation: "vertical"
        size: root.size
    
        GridLayout:
            id: board_grid
            size: root.size
            
        Label:
            id: state_label
            height: 90
''')


class TurnBasedGameClient(Screen):
    
    #kivy string property indicating the target network address
    target_address = StringProperty()
    
    #called by Kivy when the screen is entered (displayed)
    def on_enter(self):
        self.target_game = TurnBasedGameList.get_game_from_name(self.target_address)
        
        #create the grid of buttons
        self.create_grid()
        
        #update the button display before starting the game
        #needed for some games when the start position is not empty
        self.update_display()
        
        self.ids["state_label"].text = "Waiting opponent"
        
        #game state
        self.play_turn = False
        self.player_id = 0
        
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message, connection_made_callback = self.connection_made)
    
    def create_grid(self):
        rows = self.target_game.rows()
        cols = self.target_game.cols()
        cell_width, cell_height = self.target_game.cell_size()
        
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
        message = Network_Message(self.target_address, "ENTER", "")
        self.network_interface.send(message)
        
    def receive_message(self, message):
        #print(message.to_bytes())
        if message.network_command == "SET_PLAYER_ID":
            self.player_id = int(message.message_content)
        elif message.network_command == "REQUEST_MOVE":
            self.play_turn = True
            self.ids["state_label"].text = "Your turn"
        elif message.network_command == "WAIT_OPP_MOVE":
            self.ids["state_label"].text = "Opponent turn"
        elif message.network_command == "PLAYER1_MOVE":
            move = int(message.message_content)
            self.target_game.play(move, player=1)
            self.update_display()
        elif message.network_command == "PLAYER2_MOVE":
            move = int(message.message_content)
            self.target_game.play(move, player=2)
            self.update_display()
        elif message.network_command == "GAME_FINISHED":
            self.ids["state_label"].text = "Game finished"
            winner = int(message.message_content)
            
            if winner == 0:
                win_result = "Draw"
            elif winner == self.player_id:
                win_result = "You Win"
            else:
                win_result = "You Lose"
            
            popup = Popup(title='Game finished',
                          content=Label(text=win_result),
                          size_hint=(None, None), size=(200, 200))
            popup.open()
    
    def cell_clicked(self, button):
        #print(button.id)
        if self.play_turn:
            move = int(button.id)
            if not self.target_game.is_valid_play(move, player=self.player_id):
                return
            
            self.play_turn = False
            message = Network_Message(self.target_address, "MOVE", button.id)
            self.network_interface.send(message)
    
    def update_display(self):
        #update all the buttons (at least for now and for usual board games, this is not too heavy)
        rows = self.target_game.rows()
        for i in range(rows):
            for j in range(self.target_game.cols()):
                self.button_list[i*rows+j].text = self.target_game.get_label(i, j)
