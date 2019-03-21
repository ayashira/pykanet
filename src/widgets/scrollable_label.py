from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.properties import StringProperty, ListProperty
from kivy.lang import Builder

from kivy.uix.boxlayout import BoxLayout

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
        on_ref_press: root.link_clicked(args[1])
        canvas.before:
            Color:
                rgba: root.bcolor
            Rectangle:
                pos: self.pos
                size: self.size
''')

#default text to None, default background to white
class ScrollableLabel(ScrollView):
    
    #add an event triggered when a link other than http link is clicked
    __events__ = ScrollView.__events__ + ('on_link_clicked',)
    
    text = StringProperty('')
    bcolor = ListProperty([1,1,1,1])
    
    #format the links in some text string, with the markup language of kivy
    #note: probably not the best place in the code for this function (should be independent of the label object)
    def format_links(self, text_str):
        #use a regular expression to add kivy color and ref markup around web addresses
        text_str = re.sub(r'(https?:\S*)', r'[color=0000ff][u][ref=\1]\1[/ref][/u][/color]', text_str, flags=re.MULTILINE)
        return text_str
    
    #format the wiki syntax to kivy markup language
    def format_wiki_syntax(self, text_str):
        #use a regular expression to add kivy color and ref markup around web addresses
        text_str = re.sub(r'(https?:\S*)', r'[color=0000ff][u][ref=\1]\1[/ref][/u][/color]', text_str, flags=re.MULTILINE)
        
        #kivy color and ref markup for [[ ]] links
        text_str = re.sub(r'\[\[(\S*)\]\]', r'[color=0000ff][u][ref=\1]\1[/ref][/u][/color]', text_str, flags=re.MULTILINE)
        
        return text_str
        
    def link_clicked(self, link):
        if link.startswith("http"):
            import webbrowser
            webbrowser.open(link)
        else:
            self.dispatch('on_link_clicked', link)

    def on_link_clicked(self, link):
        pass

#format the links in some text string, with the markup language of kivy
#TODO : code redundancy with ScrollableLabel
def format_links(text_str):
    #use a regular expression to add kivy color and ref markup around web addresses
    text_str = re.sub(r'(https?:\S*)', r'[color=0000ff][u][ref=\1]\1[/ref][/u][/color]', text_str, flags=re.MULTILINE)
    return text_str

    
Builder.load_string('''
<CustomLabel>:
    size_hint_x: 0.8
    size_hint_y: None
    height: self.minimum_height
    orientation: "vertical"
    
    Label:
        id:minor_label
        size_hint: None, None
        size: self.texture_size
        markup:True
        text: ""
        pos_hint: {'left': 1}
    Label:
        id:text_label
        size_hint_y: None
        height: self.texture_size[1]
        text_size: self.width, None
        padding: [7, 7]
        markup:True
        on_ref_press: root.link_clicked(args[1])
        canvas.before:
            Color:
                rgba: root.bcolor
            RoundedRectangle:
                pos: self.pos
                size: self.size
''')

#default text to None, default background to white
class CustomLabel(BoxLayout):
    
    #add an event triggered when a link other than http link is clicked
    __events__ = BoxLayout.__events__ + ('on_link_clicked',)
    
    bcolor = ListProperty([1,1,1,1])
    
    def link_clicked(self, link):
        if link.startswith("http"):
            import webbrowser
            webbrowser.open(link)
        else:
            self.dispatch('on_link_clicked', link)

    def on_link_clicked(self, link):
        pass
