'''
    Custom labels to define kivy interfaces more easily
    
    FitTextLabel:
        - label size fit to test
        - no background or link support
    
    LinkLabel:
        - clickable links
        - text should be set with set_text(text, text_color)
    
    RoundedLabel:
        - inherits LinkLabel
        - rounded rectangle background   
    
    FitTextRoundedLabel:
        - inherits RoundedLabel
        - label size fit to text (intended for one-line short text)
    
    ScrollableLabel:
        - clickable http and wiki links
        - rectangle background
        - scrollable (intended for large multi-line text)
        - set_wiki_text(text, text_color)
    
    TitledLabel:
        - clickable http links
        - rounded rectangle background
        - title text above the label
'''

from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout

# to open http links in user default webbrowser
import webbrowser

# for regular expressions
import re

# format the links in some text string, with the markup language of kivy
def format_links(text_str):
    # use a regular expression to add kivy color and ref markup around web addresses
    text_str = re.sub(r'(https?:\S*)', r'[color=0000ff][u][ref=\1]\1[/ref][/u][/color]', text_str, flags=re.MULTILINE)
    return text_str

# format the wiki syntax to kivy markup language
def format_wiki_syntax(text_str):
    # use a regular expression to add kivy color and ref markup around web addresses
    text_str = re.sub(r'(https?:\S*)', r'[color=0000ff][u][ref=\1]\1[/ref][/u][/color]', text_str, flags=re.MULTILINE)
    
    # kivy color and ref markup for [[ ]] links
    text_str = re.sub(r'\[\[(\S*)\]\]', r'[color=0000ff][u][ref=\1]\1[/ref][/u][/color]', text_str, flags=re.MULTILINE)
    
    return text_str


Builder.load_string('''
<FitTextLabel>:
    size_hint: None, None
    size: self.texture_size
''')

class FitTextLabel(Label):
    '''
        Label with size fitted to text (for short text labels).
        No background or link support .
    '''
    pass

    
Builder.load_string('''
<LinkLabel>:
    markup: True
    text: ""
    on_ref_press: self.link_clicked(args[1])
''')
    
class LinkLabel(Label):    
    '''
        Link Label : Label with http link support
        
        When an http link is clicked, client default browser is opened.
        When a wiki link is clicked, a custom event 'on_link_clicked' is triggered.
        
        set_text(text, text_color) : set the text of the label with a given color string
    '''
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_link_clicked')
    
    def set_text(self, text, text_color=None):
        if text_color:
            self.text = "[color=" + text_color + "]" + format_links(text) + "[/color]"
        else:
            self.text = format_links(text)
    
    # called when a [ref] [/ref] link is clicked in the label
    def link_clicked(self, link):
        if link.startswith("http"):
            webbrowser.open(link)
        else:
            self.dispatch('on_link_clicked', link)
    
    def on_link_clicked(self, link):
        pass


Builder.load_string('''
<RoundedLabel>:
    padding: [7, 7]
    
    canvas.before:
        Color:
            rgba: root.bcolor
        RoundedRectangle:
            pos: self.pos
            size: self.size
''')
    
class RoundedLabel(LinkLabel):     
    '''
        Rounded Label
          - same as Link Label (support http links)
          - uniform color rounded rectangle background 
        
        Background color can be set with bcolor property
    '''
    
    bcolor = ListProperty([1,1,1,1])


Builder.load_string('''
<FitTextRoundedLabel>:
    size_hint: None, None
    size: self.texture_size
''')

class FitTextRoundedLabel(RoundedLabel):
    '''
        Rounded Label with size fitted to text (for short text labels)
    '''
    
    pass


Builder.load_string('''
<ScrollableLabel>:
    scroll_y:0
    LinkLabel:
        size_hint_y: None
        height: max(self.texture_size[1], root.size[1])
        text_size: self.width, None
        text: root.text
        on_link_clicked: root.dispatch('on_link_clicked', args[1])
        canvas.before:
            Color:
                rgba: root.bcolor
            Rectangle:
                pos: self.pos
                size: self.size
''')

# default text to "", default background to white
class ScrollableLabel(ScrollView):
    '''
        Scrollable Label
          - support http and wiki links
          - wiki links trigger a custom event on_link_clicked 
          - label is scrollable
          - uniform color rectangle background
          - background color can be set with bcolor property
    '''
    
    text = StringProperty('')
    bcolor = ListProperty([1,1,1,1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_link_clicked')
    
    def set_wiki_text(self, text, text_color=None):
        if text_color:
            self.text = "[color=" + text_color + "]" + format_wiki_syntax(text) + "[/color]"
        else:
            self.text = format_wiki_syntax(text)
    
    def on_link_clicked(self, link):
        pass


Builder.load_string('''
<TitledLabel>:
    size_hint_y: None
    height: self.minimum_height
    orientation: "vertical"
    
    LinkLabel:
        id:title_label
        size_hint: None, None
        size: self.texture_size
        markup:True
        text: ""
        pos_hint: {'left': 1}
    RoundedLabel:
        id:text_label
        bcolor: root.bcolor
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        on_link_clicked: root.dispatch(args[1])
''')

# default text to None, default background to white
class TitledLabel(BoxLayout):
    '''
        Rounded Label with a title above
          - support http links in both the main label and title label
          - background color can be set with bcolor property
          - set_text(text, text_color) : set the text of the main label 
          - set_title_text(text, text_color) : set the text of the title label
    '''
    
    bcolor = ListProperty([1,1,1,1])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_link_clicked')
    
    def set_text(self, text, text_color=None):
        self.ids["text_label"].set_text(text, text_color)
    
    def set_title_text(self, text, text_color=None):
        self.ids["title_label"].set_text(text, text_color)
    
    def title_to_right(self):
        self.ids["title_label"].pos_hint = {'right': 1}
    
    def on_link_clicked(self, link):
        pass
