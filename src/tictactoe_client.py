from network_interface import *

from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

from kivy.uix.screenmanager import Screen, NoTransition
from kivy.properties import StringProperty
from kivy.lang import Builder

from scrollable_label import ScrollableLabel
from shift_enter_textinput import ShiftEnterTextInput

Builder.load_string('''
<TicTacToeClient>:
    GridLayout:
        id: board_grid
        size: root.size
        rows: 3
        cols: 3
''')


class TicTacToeClient(Screen):
    
    #kivy string property indicating the target network address
    target_address = StringProperty()
    
    #called by Kivy when the screen is entered (displayed)
    def on_enter(self):
        self.create_grid(self.ids["board_grid"].rows, self.ids["board_grid"].cols)
        
        #game state
        self.play_turn = False
        
        self.network_interface = NetworkInterface(data_received_callback = self.receive_message, connection_made_callback = self.connection_made)
    
    def create_grid(self, rows, cols):
        for i in range(rows):
            for j in range(cols):
                button = Button(text='', width=80, height=80, size_hint=(None, None), id=str(i*rows+j))
                button.bind(on_press=self.cell_clicked)
                self.ids["board_grid"].add_widget(button)
    
    def connection_made(self):
        #connection is established, connect to the target address
        message = Network_Message("dummy_user", self.target_address, "ENTER", "")
        self.network_interface.network_send(message)
        
    def receive_message(self, message):
        print(message.to_bytes())
        if message.network_command == "REQUEST_MOVE":
            self.play_turn = True
        
    
    def cell_clicked(self, button):
        #print(button.id)
        if self.play_turn:
            self.play_turn = False
            message = Network_Message("dummy_user", self.target_address, "MOVE", button.id)
            self.network_interface.network_send(message)
