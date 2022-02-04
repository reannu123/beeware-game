"""
My first application
"""

import toga
from toga.style import Pack
from toga.style.pack import *
from toga.constants import *
from .gameobjects import *


class WordleClone(toga.App):
    
    def startup(self):
        

        # Whole Game Screen
        self.game_box = MainWordleGame(caller = self, actions = [self.show_dialog])

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.game_box
        self.main_window.show()


    # Allows classes to access window dialog boxes easily
    def show_dialog(self, widget, type, title, text):
        if (type == 1):
            self.main_window.error_dialog(title,text)
        elif(type == 2):
            self.main_window.info_dialog(title,text)
        elif(type == 3):
            return self.main_window.confirm_dialog(title,text)
            
def main():
    return WordleClone()
