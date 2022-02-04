from ctypes import alignment
import toga
from toga.style import Pack
from toga.style.pack import *
from toga.constants import * 
import random
import string

class WordButton(toga.Button):
    def __init__(self, label='', id=None, on_press=None, enabled=True, factory=None):
        
        self.style = Pack(padding = 2, height = 50, width = 50, background_color = "gray")
        super().__init__(label, id, self.style, on_press, enabled, factory)

class GameRow(toga.Box):
    def __init__(self, id=None, children=None, factory=None):
        self.style = Pack(direction = ROW, alignment = CENTER, padding = (3,0))
        super().__init__(id=id, style=self.style, factory=factory, children = children)

class GameColumn(toga.Box):
    def __init__(self, id=None, children=None, factory=None):
        self.style = Pack(direction = COLUMN, alignment = CENTER, padding = (3,0))
        super().__init__(id=id, style=self.style, factory=factory, children = children)

class GameButtonRow(GameColumn):
    def __init__(self, button_label = '', id=None,factory=None, action = None):
        self.button = toga.Button(button_label,on_press=action, style = Pack(flex = 1))
        super().__init__(id=id, factory=factory, children = [self.button])

class GameInputDiv(GameColumn):
    def __init__(self, input_label = '',button_label = '', id=None, style=None, factory=None, action = None):
        
        self.text_input_label = toga.Label(input_label, style=Pack(padding=(0, 5)))
        self.text_input = toga.TextInput(style = Pack(flex = 1, padding = (0,5)))

        self.input_row = GameRow()
        self.input_row.add(self.text_input_label)
        self.input_row.add(self.text_input)

        
        self.button = toga.Button(button_label, on_press = action, style = Pack(padding=(0, 5), flex = 1))
        self.button_row = GameRow()
        self.button_row.add(self.button)

        super().__init__(id=id, factory=factory, children = [self.input_row, self.button_row])

class WordRow(toga.Box):
    def __init__(self, id=None,  factory=None, wordLen=1):
        self.style = Pack(direction = ROW)
        self.wordSet = [WordButton() for i in range(wordLen)]
        super().__init__(id=id, style = self.style, children = self.wordSet, factory=factory)

class LabelRow(GameRow):
    def __init__(self, label = None, id=None, style=None, factory=None):
        super().__init__(id=id, factory=factory)
        self.text = label
        self.label = toga.Label(self.text)
        self.add(self.label)
        

class MainWordleGame(toga.Box):
    def __init__(self, caller = None, id=None, style=None, factory=None,actions = None):
        super().__init__(id=id, style=style, factory=factory)

        self.caller = caller
        self.style = style=Pack(direction = COLUMN, alignment = CENTER)
        self.gameOver = False
        self.guessCount = 0
        self.wordLen = 5
        self.numOfRows = 6
        self.actions = actions
        self.hint_used = 0
        self.guesses_path = "/wordle-allowed-guesses.txt"
        self.answers_path = "/wordle-answers-alphabetical.txt"
        self.words = []
        self.correctWord = ""
        self.answers = []

        # Word Caching
        self.word_cache(self)
        

        # Main UI
        ## Game Input Div
        self.guess_box = GameInputDiv(input_label = "Guess: ", button_label = "Guess", action = self.guess)

        ## Alphabet Row
        self.alphabet_row = LabelRow('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z')


        ## Words Entered (Trials) Row
        
        self.word_rows = [WordRow(wordLen = self.wordLen) for i in range(self.numOfRows)]
        self.words_box = GameColumn(children = self.word_rows)
        self.trials_row = GameRow(children = [self.words_box])


        ## Restart Button Row
        self.restart_row = GameButtonRow(button_label = "Restart", action = self.restart)


        # Adding to Main Wordle Game
        self.add(self.guess_box)
        self.add(self.alphabet_row)
        self.add(toga.Box(style = Pack(flex = 1)))
        self.add(self.trials_row)
        self.add(toga.Box(style = Pack(flex = 1)))
        self.add(self.restart_row)


        # Special Hint Functionality
        cmd1 = toga.Command(
        self.hint,
        label='Hint',
        tooltip='Take a hint!',
        order=1
        )

        self.caller.commands.add(cmd1)

    def guess(self, widget):
        
        playerInput = self.guess_box.text_input.value.lower()
        alphabet = list(string.ascii_lowercase)
        validInput = True

        for i in playerInput:
            if(i not in alphabet):
                validInput = False
                break

        # is game Over?
        if(self.gameOver):
            self.gameover_prompt(self)
            return 0

        # is input length != 5?
        if(len(playerInput) != 5):
            if(len(playerInput)==0):
                playerInput = "Input"
            
            self.actions[0](self.caller, 1,"Invalid Word Length!",'{} does not have 5 alphabet characters!'.format(playerInput))
            self.guess_box.text_input.value = ""
            return 0
            
        # does input have non-alphabet?
        if(validInput == False):
            self.actions[0](self.caller,1, 'Invalid Word!','{} has unsupported characters!'.format(playerInput))
            self.guess_box.text_input.value = ""
            return 0

        # is input not in allowed guesses?
        if(playerInput not in self.words and playerInput not in self.answers and playerInput != self.correctWord):
            self.actions[0](self.caller, 1, 'Invalid Word!', '{} is not a valid word!'.format(playerInput.upper()))
            self.guess_box.text_input.value = ""
            return 0
        
        # is input in allowed guesses?
        if(playerInput in self.words or playerInput in self.answers and playerInput != self.correctWord):
            for i in range(len(playerInput)):
                color = "gray"
                self.word_rows[self.guessCount].wordSet[i].label = playerInput[i].upper()
                if (playerInput[i] == self.correctWord[i]):
                    color = "green"
                elif(playerInput[i] in self.correctWord):
                    color = "yellow"
                self.word_rows[self.guessCount].wordSet[i].style.background_color = color
            
            self.guessCount += 1
            if(self.guessCount == self.numOfRows):
                self.gameOver = True
                self.actions[0](self.caller, 1, "Game Over!",'{} was the answer!'.format(self.correctWord.upper()))
                self.gameover_prompt(self)
            self.guess_box.text_input.value = ""
            return 0



        # is input correct?
        if(playerInput == self.correctWord):
            for i in range(len(playerInput)):
                self.word_rows[self.guessCount].wordSet[i].label = playerInput[i].upper()
                self.word_rows[self.guessCount].wordSet[i].style.background_color = "green"
            self.gameOver = True
            self.actions[0](self.caller, 2, "Congratulations!",'{} is correct!'.format(playerInput.upper()))
            self.guess_box.text_input.value = ""
            self.gameover_prompt(self)
            return 0
        
            
        

    def restart(self, widget):
        print("Restarted Game")
        self.gameOver = False
        self.guessCount = 0
        self.hint_used = 0
        self.guess_box.text_input.value = ""

        self.correctWord = self.answers[random.randint(0, len(self.answers))]
        for i in range(0,self.numOfRows):
            for j in range(0,self.wordLen):
                self.word_rows[i].wordSet[j].label = ""
                self.word_rows[i].wordSet[j].style.background_color = "gray"

        self.actions[0](self.caller, 2, "New Game!",'Game is restarted!')
    
    def hint(self, widget):
        if (self.gameOver):
            self.gameover_prompt(self)
            return 
        self.hint_used += 1
        text = ""
        if(self.hint_used == 1):
            text = "The first letter is: " + self.correctWord[0].upper()
        elif(self.hint_used == 2):
            text = "The second letter is: " + self.correctWord[1].upper()
        elif(self.hint_used == 3):
            text = "The third letter is: " + self.correctWord[2].upper()
        elif(self.hint_used == 4):
            text = "The fourth letter is: " + self.correctWord[3].upper()
        elif(self.hint_used == 5):
            text = "The fifth letter is: " + self.correctWord[4].upper()

        self.actions[0](self.caller, 2, "Hint {}".format(self.hint_used),text)

        if(self.hint_used == 5):
            self.actions[0](self.caller, 1, "ALL HINTS USED","You now know the word! \n{}".format(self.correctWord.upper()))
            self.restart(self)
    
    def gameover_prompt(self, widget):
        if(self.actions[0](self.caller, 3, "Game is over!",'Do you want to restart the game?')):
            self.restart(self)

    def word_cache(self, widget):
        allowed_guesses_file = open(str(self.caller.paths.app)+ self.guesses_path,"r") 
        self.words = [i[:-1] for i in allowed_guesses_file]
        allowed_guesses_file.close()

        answers_file = open(str(self.caller.paths.app)+ self.answers_path,"r")
        self.answers = [i[:-1] for i in answers_file]
        answers_file.close()

        self.correctWord = self.answers[random.randint(0, len(self.answers))]