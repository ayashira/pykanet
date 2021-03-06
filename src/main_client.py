import sys
import argparse
import os

# function to parse command line arguments
def parse_arguments():
    # --use_localhost can be used to force the connection to localhost instead of the real distant server
    # this is useful mainly for tests
    parser = argparse.ArgumentParser()
    parser.add_argument('-lh', '--use_localhost', action='store_true')
    parser.add_argument('-og', '--opengl_config', action='store_true')
    
    # parse only the known arguments, and leave the others for kivy parser
    args, unknown = parser.parse_known_args()
    sys.argv[1:] = unknown
    
    return args

# this is not a good practice to parse arguments here instead of __main__
# this is a workaround to strange kivy design that parses arguments directly and silently inside import
custom_args = parse_arguments()

# if opengl_custom, the following flags can be customized here
# maybe it helps to launch Kivy on some old machines (not sure)
if custom_args.opengl_config:
    print("Using customized environment flags")
    os.environ['KIVY_GLES_LIMITS'] = '1'
    os.environ['USE_OPENGL_MOCK'] = '0'
    os.environ['USE_OPENGL_ES2'] = '0'
    os.environ['USE_SDL2'] = '0'

# disable mouse emulation of multitouch
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

# start the kivy-compatible twisted reactor
from kivy.support import install_twisted_reactor
install_twisted_reactor()

from kivy.app import App
from apps.desktop_client import DesktopClient

# currently needed to set localhost
from network_interface import NetworkInterface

# Kivy does not include fonts supporting japanese
# A font file must be provided manually
# NOTO font downloaded from here: https://www.google.com/get/noto/help/cjk/
utf8_font_path = "NotoSansCJK-Regular.ttc"

# Main App with a screen manager
class MainClient(App):

    def build(self):
        return DesktopClient()

if __name__ == '__main__':
    # note: command-line arguments are parsed at top of file, before kivy import
    if custom_args.use_localhost:
        NetworkInterface.set_server_to_localhost()
    
    MainClient().run()
