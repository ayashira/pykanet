from network_interface import NetworkInterface
from network_message import NetworkMessage

from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label

from kivy.properties import StringProperty, BooleanProperty
from kivy.lang import Builder

from apps.turnbasedgame_list import TurnBasedGameList

from kivy.clock import Clock

from kivy.graphics import Color
from kivy.properties import NumericProperty


Builder.load_string('''
<TurnBasedGameClient>:
    StackLayout:
        orientation: "lr-tb"
        size: root.size
        pos: root.pos

        GridLayout:
            id: board_grid
            size_hint: None, None
            height:self.minimum_height
            width:self.minimum_width

        BoxLayout:
            orientation: "vertical"
            size_hint: None, None
            height: self.minimum_height
            width: self.minimum_width
            pos_hint:{'top':1, 'left': 1}
            
            BoxLayout:
                orientation: "horizontal"
                size_hint: None, None
                height: self.minimum_height
                width: self.minimum_width
                pos_hint: {'top':1, 'center_x':0.5}
                spacing: 2

                BoxLayout:
                    id: user_frame
                    orientation: "vertical"
                    size_hint: None, None
                    height: self.minimum_height
                    width: self.minimum_width
                    spacing: 2
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 0
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                        
                    Label:
                        id: user_label
                        size_hint: None, None
                        pos_hint: {'top':1, 'center_x':0.5}
                        size: max(80, self.texture_size[0]),self.texture_size[1]

                    Label:
                        id: user_timer_label
                        size_hint: None, None
                        pos_hint: {'top':0, 'center_x':0.5}
                        size: max(80, self.texture_size[0]),self.texture_size[1]

                BoxLayout:
                    id: opp_user_frame
                    orientation: "vertical"
                    size_hint: None, None
                    size: self.minimum_width, self.minimum_height
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 0
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            
                    spacing: 2

                    Label:
                        id: opp_user_label
                        size_hint: None, None
                        pos_hint: {'top':1, 'center_x':0.5}
                        size: max(80, self.texture_size[0]),self.texture_size[1]

                    Label:
                        id: opp_timer_label
                        size_hint: None, None
                        pos_hint: {'top':0, 'center_x':0.5}
                        size: max(80, self.texture_size[0]),self.texture_size[1]
            Label:
                id: state_label
                size_hint: None, None
                size: self.texture_size
                pos_hint: {'top':1, 'center_x':0.5}
            BoxLayout:
''')



class TurnBasedGameClient(Screen):
    
    # kivy string property indicating the target network address
    target_address = StringProperty()

    # allotted time
    allotted_time = NumericProperty(0)
    opp_allotted_time = NumericProperty(0)

    
    # called by Kivy when the screen is entered (displayed)
    def on_enter(self):
        self.target_game = TurnBasedGameList.get_game_from_name(self.target_address)
        
        # create the grid of buttons
        self.create_grid()
       
        # update the button display before starting the game
        # needed for some games when the start position is not empty
        self.update_display()
        self.ids["state_label"].text = "Waiting opponent"

        # initial user name and set clock
        self.user_name = ""
        self.opp_user_name = ""
        self.init_user_frame()
        self.set_timer()
        # game state
        self.play_turn = False
        self.player_id = 0
        self.network_interface = NetworkInterface(client = self)
        self.network_interface.send(self.target_address, "ENTER", "")
    
    def create_grid(self):
        # remove all existing buttons (current client on_enter() can be called multiple times)
        self.ids["board_grid"].clear_widgets()
        
        # initialize the grid rows and cols
        rows = self.target_game.rows()
        cols = self.target_game.cols()
        cell_width, cell_height = self.target_game.cell_size()
        
        self.ids["board_grid"].rows = rows
        self.ids["board_grid"].cols = cols
        
        # list of buttons used to access buttons from an index
        self.button_list = []
        
        for i in range(rows):
            for j in range(cols):
                # buttons are identified with coords value
                button = Button(text='', width=cell_width, height=cell_height, size_hint=(None, None))
                button.coords = (i, j)
                button.bind(on_press=self.cell_clicked)
                self.ids["board_grid"].add_widget(button)
                self.button_list.append(button)

    def set_timer(self):
        # setting timer(for timeout)
        if 'allotted_time' not in dir(self.target_game):
            self.is_allotted_time = False
        else:
            limit_time = self.target_game.allotted_time()
            if limit_time == -1:
                self.is_allotted_time = False
                pass
            else:
                self.is_allotted_time = True
                # Note: the unit of allotted time is minute.
                self.allotted_time = limit_time * 60.0
                self.opp_allotted_time = limit_time * 60.0
                # set trigger timer
                self.cb = Clock.create_trigger(self.on_countdown, 1, interval=True)
                self.opp_cb = Clock.create_trigger(self.on_opp_countdown, 1, interval=True)
    
    def receive_message(self, message):
        if message.command == "SET_PLAYER_ID":
            self.player_id = int(message.content)
        elif message.command == "REQUEST_MOVE":
            opp_time = message.content

            # user timer counts on client.
            # the server send the time where the move is received
            # opponent timer freezes
            if self.is_allotted_time:
                self.opp_cb.cancel()
                self.cb()
                if opp_time is not "":
                    opp_time = float(opp_time)
                    self.opp_allotted_time = opp_time

                self.ids["user_timer_label"].text = self.format_time(self.allotted_time)
                self.ids["opp_timer_label"].text = self.format_time(self.opp_allotted_time)

            self.ids["state_label"].text = "Your turn"
            self.play_turn = True
            self.draw_active_frame()
        elif message.command == "WAIT_OPP_MOVE":
            time = message.content

            # opponent timer counts on clienct server.
            # user timer freezes
            if self.is_allotted_time:
                self.cb.cancel()
                self.opp_cb()
                if time is not "":
                    time = float(time)
                    self.allotted_time = time

                self.ids["opp_timer_label"].text = self.format_time(self.opp_allotted_time)
                self.ids["user_timer_label"].text = self.format_time(self.allotted_time) 

            self.ids["state_label"].text = "Opponent turn"
            self.draw_inactive_frame()
        elif message.command == "PLAYER1_MOVE":
            move = message.content
            self.target_game.play(move, player=1)
            self.update_display()
        elif message.command == "PLAYER2_MOVE":
            move = message.content
            self.target_game.play(move, player=2)
            self.update_display()
        elif message.command == "SET_USER_NAMES":
            self.user_name, self.opp_user_name = message.content
            user_text = ("O", "x") if self.player_id == 1 else ("x", "O")
            self.ids["user_label"].text = self.user_name +  " : " + user_text[0]
            self.ids["opp_user_label"].text = self.opp_user_name + " : " + user_text[1]
        elif message.command == "GAME_FINISHED":
            self.ids["state_label"].text = "Game finished"
            winner = message.content
            
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
        if self.play_turn:
            move = button.coords
            if not self.target_game.is_valid_play(move, player=self.player_id):
                return
            
            self.play_turn = False
            time = str(self.allotted_time) if self.is_allotted_time else ""
            self.network_interface.send(self.target_address, "MOVE", [time, move])
    
    def update_display(self):
        # update all the buttons (at least for now and for usual board games, this is not too heavy)
        rows = self.target_game.rows()
        for i in range(rows):
            for j in range(self.target_game.cols()):
                self.button_list[i*rows+j].text = self.target_game.get_label(i, j)
    
    def format_time(self, remaining_time):
        return str(int(remaining_time // 60)).zfill(2) + " : " + str(int(remaining_time % 60)).zfill(2)
    
    def on_countdown(self, *args):
         if not self.is_allotted_time:
             pass
         if self.allotted_time > 0:
             self.allotted_time -= 1.0
         else:
             self.network_interface.send(self.target_address, "TIMEOUT", "")
             self.allotted_time = 0
         self.ids["user_timer_label"].text = self.format_time(self.allotted_time)
    
    def on_opp_countdown(self, *args):
        if not self.is_allotted_time:
                pass
        if self.opp_allotted_time > 0:
            self.opp_allotted_time -= 1.0
        else:
            self.opp_allotted_time = 0

        self.ids["opp_timer_label"].text = self.format_time(self.opp_allotted_time)
    
    def draw_active_frame(self):
        self.ids["user_frame"].canvas.before.children[0] = Color(1, 1, 1, 1)
        self.ids["opp_user_frame"].canvas.before.children[0] = Color(0, 135/255, 173/255, 1)
        self.ids["user_label"].color = (0/255, 95/255, 133/255, 1)
        self.ids["user_timer_label"].color = (0/255, 95/255, 133/255, 1)
        self.ids["opp_user_label"].color = (69/255, 173/255, 213/255, 1)
        self.ids["opp_timer_label"].color = (69/255, 173/255, 213/255, 1)
    
    
    def init_user_frame(self):
        self.ids["user_label"].text = " "
        self.ids["user_timer_label"].text = " "
        self.ids["opp_user_label"].text = " "
        self.ids["opp_timer_label"].text = " "


    def draw_inactive_frame(self):
        self.ids["user_frame"].canvas.before.children[0] = Color(0, 135/255, 173/255, 1)
        self.ids["opp_user_frame"].canvas.before.children[0] = Color(1, 1, 1, 1)
        self.ids["user_label"].color = (69/255, 173/255, 213/255, 1)
        self.ids["user_timer_label"].color = (69/255, 173/255, 213/255, 1)
        self.ids["opp_user_label"].color = (0/255, 95/255, 133/255, 1)
        self.ids["opp_timer_label"].color = (0/255, 95/255, 133/255, 1)

