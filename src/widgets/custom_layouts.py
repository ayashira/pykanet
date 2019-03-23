'''
    Custom layouts to define kivy interfaces more easily
   
    ScrollableVBoxLayout:
        - scrollable vertical box layout
        - convenient functions to add widgets at the top/bottom
           with horizontal alignment on the left/center/right
'''

from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout

from kivy.lang import Builder


Builder.load_string('''
<ScrollableVBoxLayout>:
    scroll_y:0
    BoxLayout:
        id: main_layout
        orientation: "vertical"
        size_hint_y: None
        height: self.minimum_height
        padding: [12, 0, 12, 0]
        spacing: 5
''')
    
class ScrollableVBoxLayout(ScrollView):    
    '''
        Scrollable vertical box layout
    '''
    
    def clear(self):
        self.ids["main_layout"].clear_widgets()
        self.ids["main_layout"].scroll_y = 0
    
    def add(self, widget, pos = 'bottom', halign = 'left'):
        '''
            Add a widget to the layout
            pos = 'bottom' or 'top'
            halign = 'left', 'center' or 'right'
        '''
        
        if halign == 'left':
            widget.pos_hint = {'left': 1}
        elif halign == 'center':
            widget.pos_hint = {'center_x': 0.5}
        elif halign == 'right':
            widget.pos_hint = {'right': 1}
        
        insert_idx = 0 if pos == 'bottom' else len(self.ids["main_layout"].children)
        self.ids["main_layout"].add_widget(widget, insert_idx)

    def remove(self, widget):
        self.ids["main_layout"].remove_widget(widget)
