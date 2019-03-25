'''
    Custom text inputs to define kivy interfaces more easily.
   
    ShiftEnterTextInput:
        - multiple line textinput
        - Support of SHIFT+ENTER to create a newline
        - 'on_key_pressed' event when a key is pressed
'''

from kivy.uix.textinput import TextInput

class ShiftEnterTextInput(TextInput):
    '''
        TextInput on multiple line with special support of ENTER and SHIFT+ENTER:
        Enter key to validate text (triggers on_text_validate event)
        Shift+Enter key to insert a new line
        
        'on_key_pressed' is a custom event triggered when a key is pressed
    '''
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_key_pressed')
        self.multiline = True
        
    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        self.dispatch('on_key_pressed')
        
        # 'enter' key
        if keycode[0]==13:
            if 'shift' in modifiers:
                # shift+enter, add a new line
                self.insert_text(u'\n')
                return True
            else:
                # enter key only, validate the current text 
                self.dispatch('on_text_validate')
                return True
        # 'backspace' key
        elif keycode[0]==8:
            if 'ctrl' in modifiers:
                # ctrl+backspace
                # maybe something could be done here to support ctrl+backspace shortcut
                pass
        
        return super(ShiftEnterTextInput, self).keyboard_on_key_down(window, keycode, text, modifiers)

    def on_key_pressed(self):
        pass
