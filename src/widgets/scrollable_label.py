from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder

#for regular expressions
import re

#if a [ref] [/ref] link is clicked in the label, on_ref_press is called
# and we open the user default webbrowser with the ref content 

Builder.load_string('''
<ScrollableLabel>:
    scroll_y:0
    Label:
        size_hint_y: None
        height: max(self.texture_size[1], root.size[1])
        text_size: self.width, None
        text: root.text
        markup:True
        on_ref_press:
            import webbrowser
            webbrowser.open(args[1])
        canvas.before:
            Color:
                rgba: root.bcolor
            Rectangle:
                pos: self.pos
                size: self.size
''')

#default text to None, default background to white
class ScrollableLabel(ScrollView):
    text = StringProperty('')
    bcolor = ListProperty([1,1,1,1])
    
    #format the links in some text string, with the markup language of kivy
    #note: probably not the best place in the code for this function (should be independent of the label object)
    def format_links(self, text_str):
        #use a regular expression to add kivy color and ref markup around web addresses
        text_str = re.sub(r'(https?:\S*)', r'[color=0000ff][u][ref=\1]\1[/ref][/u][/color]', text_str, flags=re.MULTILINE)
        return text_str
