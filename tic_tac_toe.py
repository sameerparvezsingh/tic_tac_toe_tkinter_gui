#tic_tac_toe.py

"""Game with graphics interface using TKinter
    Author: Sameer Singh
"""

import tkinter as tk
from tkinter import font
from typing import NamedTuple
from itertools import cycle



#class to store X or O label for the player with different colors for each
class Player(NamedTuple):
    label : str
    color : str

#class to represent the coordinates of the move of a player
class Move(NamedTuple):
    row : int
    col : int 
    label : str = "" #no value as default meaning no move played on a coordinate
    
#default values
BOARD_SIZE = 3
DEFAULT_PLAYERS = (
    Player(label="X", color="blue"),
    Player(label="O", color="green")
) #a tuple of 2 players

#class to represent main game login
class TicTacToeGame:
    def __init__(self, players=DEFAULT_PLAYERS, board_size=BOARD_SIZE):
        self._players = cycle(players) #to cycle through the touple of 2 players
        self.board_size = board_size
        self.current_player = next(self._players)
        self.winner_combo = []
        self._current_moves = [] #to keep track of all moves made by all players
        self._has_winner = False
        self._winning_combos = [] #to compare what cell combinations are considered a win
        self._setup_board()
    
    def reset_game(self):
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col) #set all Move objects to empty by creating a new Move object with same row and column but label ="" 
        self._has_winner = False
        self.winner_combo = []

    def _get_winning_combos(self):
        rows = [
            [(move.row, move.col) for move in row]
            for row in self._current_moves
        ]# a list of list of tuples containing coordinates of rows like 00,01,02
        #print(rows)
        columns = [list(col) for col in zip(*rows)]
        #print(columns)
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        #print(first_diagonal)
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        #print(second_diagonal)
        return rows + columns + [first_diagonal, second_diagonal]


    def _setup_board(self):
        self._current_moves = [
            [Move(row,col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]#3 rows (lists) of 3 Move objects in each column for a 3x3 board
        #print(f"self._current_moves during setup= \n {self._current_moves}")
        self._winning_combos = self._get_winning_combos()
    
    def is_valid_move(self, move):
        row, col = move.row, move.col
        move_not_played = self._current_moves[row][col].label == "" #check if label is an empty string
        no_winner = not self._has_winner
        return no_winner and move_not_played
    
    def process_move(self, move):
        row,col = move.row, move.col
        self._current_moves[row][col] = move #assign input move to item ar [row][column] in list of current moves
        for combo in self._winning_combos:
            results = set(
                self._current_moves[n][m].label
                for n,m in combo
            )#retrieve all labels (X or O) from moves in current winning combinations and store as a set object in results
            #print(f"{combo} results in process_move: {results}")

            #if both X and O exist in any of the winning combinations then it is not a win, so len(results) 
            #checks that there is only one either X or Y in all three positions oa a winning combination
            #e.g. [(0, 0), (1, 0), (2, 0)] results in process_move: {'X'}
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break

    def has_winner(self):
        return self._has_winner #chec if winner or no winner
    
    def is_tied(self):
        no_winner = not self._has_winner #check if there is a winner or not
        played_moves = (
            move.label for row in self._current_moves for move in row
        )#get label of all moves
        #use all to check if all moves in _current_moves have a label different than empty string
        #no empty string means all boxes have been played, combined with if there is no winner, then game is tied
        return no_winner and all(played_moves) 
    
    def toggle_player(self):
        self.current_player = next(self._players) #since _players hold an iterator that cyclically loops over the two players,
                                                  #next() is called to get the next player
    


#class to define the graphics of the board for the game 
class TicTacToeBoard(tk.Tk): #inherited from tkinter class
    def __init__(self, game): #called immediately after the object is created to initialize it
        super().__init__() #initialize the parent class
        self.title("Tic-Tac-Toe Game") #title of the window
        self._cells = {} #dictionary to map rows and columns of the board grid
        self._game = game
        self._create_menu() #options to replay or exit
        self._create_board_display() #create the main window
        self._create_board_grid() #create the grid to play game


    def reset_board(self):
        self._game.reset_game()
        self._update_display(msg="Ready to Play?") #reset the display text at top of window
        #iterate through all buttons and reset them with no text an bg and fg color
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")
    
    def exit_win(self):
        self.destroy() #function to destroy the window on call to exit

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(
            label = "Play Again",
            command=self.reset_board
        )
        file_menu.add_separator()
        file_menu.add_command(label="EXIT", command=self.exit_win)
        menu_bar.add_cascade(label="File",menu=file_menu)
    
    def _create_board_display(self):
        display_frame = tk.Frame(master=self) #a frame to hold the game display, master=self means that game's main window will be frame's parent
        display_frame.pack(fill=tk.X) #organizing frame at top border of window. tk.X to make sure frame gets resized if window is resized
        self.display = tk.Label( 
            master = display_frame,
            text = "Ready to play?",
            font=font.Font(size=28, weight="bold")
        ) #a label inide the frame
        self.display.pack()

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color) #set color and text of button when a user clicks it
    
    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color #another version of using .config() func on Tkinter library to display a message

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():#iterate through _cells dict and check if they are in winning position
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")#set color of cells/buttons in winning configuraion to red
    
    def play(self, event):
        clicked_btn = event.widget #retrieve the object that triggered the current event ie one og the grids with specific coordinates
        row, col = self._cells[clicked_btn] #get coordinated of the clicked button 
        move = Move(row, col, self._game.current_player.label) #new move object to get the move

        #check for validity of moves and win or no win
        if self._game.is_valid_move(move):
            self._update_button(clicked_btn)
            self._game.process_move(move)
            if self._game.is_tied():
                self._update_display(msg="It's a Tie", color="red")
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f"Player {self._game.current_player.label} won!!"
                color = self._game.current_player.color
                self._update_display(msg,color)
            else:
                self._game.toggle_player() #switch to the next player as long as no win or tie
                msg = f"{self._game.current_player.label}'s turn"
                self._update_display(msg)
    
    def _create_board_grid(self):
        grid_frame = tk.Frame(master=self) #frame to contain all grids 3x3
        grid_frame.pack()

        #loop to create a 3 rows
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight=1, minsize=50) #set size of each row using weight
            self.columnconfigure(row, weight=1, minsize=75) #set size of each column using weight
            #loop to create 3 columns
            for col in range(self._game.board_size):
                button = tk.Button(
                    master = grid_frame,
                    text="",
                    font = font.Font(size=26, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="lightblue"
                )
                self._cells[button] = (row,col) #adding all buttons to the dictionary where button is the key and coordinates as value
                button.bind("<ButtonPress-1>", self.play) #bind a button click to the play() method
                button.grid(
                    row=row,
                    column=col,
                    padx=5,
                    pady=5,
                    sticky="nsew"
                )#positioning each button with grid geometry manager



def main():
    try:
        game = TicTacToeGame()
        board = TicTacToeBoard(game)
        for key,value in board._cells.items():
            print(f"{key} : {value}")
        board.mainloop()
    except:
        print(f"An error occured")

if __name__ == "__main__":
    main()
