from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder

Builder.load_string('''
<ScrollableLabel>:
    scroll_y:0
    Label:
        size_hint_y: None
        height: max(self.texture_size[1], root.size[1])
        text_size: self.width, None
        text: root.text
        bcolor: 1, 1, 1, 1
        markup:True
        canvas.before:
            Color:
                rgba: self.bcolor
            Rectangle:
                pos: self.pos
                size: self.size
''')

class ScrollableLabel(ScrollView):
    text = StringProperty('')
    bcolor = ListProperty([0,0,0,1])
