from network_interface import NetworkInterface
from network_message import NetworkMessage

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
    FloatLayout:
        size: root.size
        BoxLayout:
            orientation: "vertical"
            size_hint: None, None
            height:self.minimum_height
            width:self.minimum_width
            pos_hint:{'top':1, 'center_x': 0.5}
            spacing: 5
            Label:
                id: opp_user_label
                size_hint: None, None
                pos_hint:{'left':1}
                size: self.texture_size
            GridLayout:
                id: board_grid
                size_hint: None, None
                height:self.minimum_height
                width:self.minimum_width
                

            Label:
                id: user_label
                size_hint: None, None
                size: self.texture_size
                pos_hint:{'left':1}

            Label:
                id: state_label
                size_hint: None, None
                size: self.texture_size 
                pos_hint:{'center_x': 0.5}
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
        self.ids["user_label"].text = " "
        self.ids["opp_user_label"].text = " "
        
        #game state
        self.play_turn = False
        self.player_id = 0
        
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message, connection_made_callback = self.connection_made)

        self.user_name = ""
        self.opp_user_name = ""
    
    def create_grid(self):
        #remove all existing buttons (current client on_enter() can be called multiple times)
        self.ids["board_grid"].clear_widgets()
        
        #initialize the grid rows and cols
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
        message = NetworkMessage(self.target_address, "ENTER", "")
        self.network_interface.send(message)
        
    def receive_message(self, message):
        #print(message.to_bytes())
        if message.command == "SET_PLAYER_ID":
            self.player_id = int(message.content)
        elif message.command == "REQUEST_MOVE":
            self.play_turn = True
            self.ids["state_label"].text = "Your turn"
            self.ids["user_label"].bold = True
            self.ids["opp_user_label"].bold = False
        elif message.command == "WAIT_OPP_MOVE":
            self.ids["state_label"].text = "Opponent turn"
            self.ids["user_label"].bold = False
            self.ids["opp_user_label"].bold = True
        elif message.command == "PLAYER1_MOVE":
            move = int(message.content)
            self.target_game.play(move, player=1)
            self.update_display()
        elif message.command == "PLAYER2_MOVE":
            move = int(message.content)
            self.target_game.play(move, player=2)
            self.update_display()
        elif message.command == "SET_USER_NAMES":
            self.user_name, self.opp_user_name = message.content
            user_text = ("O", "x") if self.player_id == 1 else ("x", "O")
            self.ids["user_label"].text = self.user_name +  " : " + user_text[0]
            self.ids["opp_user_label"].text = self.opp_user_name + " : " + user_text[1]
        elif message.command == "GAME_FINISHED":
            self.ids["state_label"].text = "Game finished"
            winner = int(message.content)
            
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
            message = NetworkMessage(self.target_address, "MOVE", button.id)
            self.network_interface.send(message)
    
    def update_display(self):
        #update all the buttons (at least for now and for usual board games, this is not too heavy)
        rows = self.target_game.rows()
        for i in range(rows):
            for j in range(self.target_game.cols()):
                self.button_list[i*rows+j].text = self.target_game.get_label(i, j)
