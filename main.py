import random
import re
from time import sleep


class Board:
    def __init__(self):
        # quit_game & restart vars are present inside of the class in case user wants to quit during one of the
        # interfaces or they want to change dim/bombs, which would require the whole game to restart. However, the game
        # itself will mostly use its own quit_game * restart_game vars to control whether the game is quit
        self.quit_game = False
        self.restart_game = False

        # Set the dimension size & number of bombs
        self.dim_size = self.set_dim_size()
        self.num_bombs = self.set_num_bombs()

        # Set symbols
        # All symbols must be len 3 for __str__ function printing
        self.symbols = {'bomb': ' X ', 'undug spot': ' - ', 'no surrounding bombs': '   ', 'flag': ' • '}

        # Initialize board to None and we'll run Board.make_new_board() at the top of each game so a new board
        # is created each time
        self.board = None

        # Initialize a set to keep track of which locations have been dug using (row, col) tuples
        self.dug = set()  # if we dig at 0,0, then self.dug = {(0,0)}

    def set_dim_size(self):
        if not self.quit_game:

            print("\nWhat size square board would you like to play on? (e.g. enter '10' for a 10x10 board).")
            while True:
                dimension_input = input("> ")
                try:
                    # Check if user wants to quit
                    if dimension_input.lower().strip() == "quit":
                        self.quit_game = True
                        break

                    # Otherwise, check that the input is a valid dimension size
                    dim = int(dimension_input)
                    if dim <= 0:  # Dim needs to be greater than 0
                        raise ValueError

                    # If no errors are raised, return dim
                    return dim

                except ValueError:
                    print("Please enter an integer that is greater than 0 and less than 1000.")

    def set_num_bombs(self):
        if not self.quit_game:

            print(f"How many bombs would you like to have on your board?"
                  f"\nFor an easy game, I'd suggest: {(self.dim_size ** 2) * 1 // 10} - {(self.dim_size ** 2) * 15 // 100} bombs."
                  f"\nFor a medium game, I'd suggest: {(self.dim_size ** 2) * 2 // 10} - {(self.dim_size ** 2) * 3 // 10} bombs."
                  f"\nFor a hard game, I'd suggest: {(self.dim_size ** 2) * 45 // 100} - {(self.dim_size ** 2) * 5 // 10} bombs.")
            while True:
                bombs_input = input("> ")
                try:
                    # Check if user wants to quit
                    if bombs_input.lower().strip() == "quit":
                        self.quit_game = True
                        break

                    # Otherwise, check that bomb input is a valid integer
                    bombs = int(bombs_input)
                    if bombs <= 0 or bombs >= self.dim_size ** 2:
                        raise ValueError

                    # If no errors are raised, return the number of bombs
                    return bombs

                except ValueError:
                    print(f"Please enter an integer that is greater than 0 but less than {self.dim_size ** 2}.")

    # Call this function at the start of each game to create a new board
    def make_new_board(self):
        # Construct a new board based on the dim size & num bombs
        # We should construct the list of lists here (or whatever representation you prefer, but since we have a 2D
        # board, list of lists is more natural).

        # Each element in the innermost list (so, each 'spot') is a 3-element dictionary where 'is bomb' tracks whether
        # the spot is a bomb, 'surrounding bombs' holds the number of surrounding bombs (if spot isn't a bomb), and
        # 'flagged' tracks whether the spot has been flagged or not
        board = [[{'is bomb': False, 'surrounding bombs': None,
                   'flagged': False} for i in range(self.dim_size)] for j in range(self.dim_size)]

        # Plant bombs
        bombs_planted = 0
        while bombs_planted < self.num_bombs:
            spot = random.randint(0, self.dim_size ** 2 - 1)
            row = spot // self.dim_size
            col = spot % self.dim_size

            if board[row][col]['is bomb']:
                continue
            board[row][col]['is bomb'] = True
            bombs_planted += 1

        # Assign the created board to self.board
        self.board = board
        # Now assign the values to the board
        self.assign_values_to_board()

    # Helper for make_new_board to assign values to each spot (values 0-8 for bombs, nothing if spot['is_bomb'] == True)
    def assign_values_to_board(self):

        # Go through each spot on the board
        for r in range(self.dim_size):
            for c in range(self.dim_size):

                # If spot contains a bomb, don't waste time assigning it a 'surrounding bombs' value
                if self.board[r][c]['is bomb']:
                    continue

                # Otherwise, assign the value of the num of surrounding bombs
                self.board[r][c]['surrounding bombs'] = self.get_num_surrounding_bombs(r, c)

    # Helper for assign_value_to_board that counts the number of bombs surrounding a specific spot
    def get_num_surrounding_bombs(self, row, col):
        # Initialize counter for number of bombs
        bomb_count = 0

        # For each of the 8 squares around that spot, if there's a bomb, increment counter by +1
        # We don't want the range to go below 0 or above dim size (since range will go up to dim size - 1)
        for surrounding_row in range(max(0, row - 1), min(self.dim_size, (row + 1) + 1)):
            for surrounding_col in range(max(0, col - 1), min(self.dim_size, (col + 1) + 1)):

                # We don't want to count the spot itself--just its surrounding spots
                if surrounding_row == row and surrounding_col == col:
                    continue
                if self.board[surrounding_row][surrounding_col]['is bomb']:
                    bomb_count += 1

        return bomb_count

    # Call this function at end of each game to reset board values so they can be created anew when the next game starts
    def reset_board(self):
        self.quit_game = False
        self.restart_game = False
        self.board = None
        self.dug = set()

    def dig(self, row, col):
        # First, let's add this spot to our set of dug places as a tuple
        self.dug.add((row, col))

        # Then we have 3 scenarios:
        # 1) There's a bomb where we dig => return False
        if self.board[row][col]['is bomb']:
            return False
        # 2) We dig a spot that's next to a bomb => we stop digging
        elif self.board[row][col]['surrounding bombs'] > 0:
            return True

        # 3) We dig a spot that's not next to a bomb and must keep digging.
        # To decide how to keep digging, we'll use the same pattern we used for checking for bombs;
        # however, we'll use recursion to dig up a bunch of spots since we're doing the same thing over and over
        for surrounding_row in range(max(0, row-1), min(self.dim_size, (row+1)+1)):
            for surrounding_col in range(max(0, col-1), min(self.dim_size, (col+1)+1)):
                if (surrounding_row, surrounding_col) in self.dug:  # If we hit a spot we've already dug, jump over it
                    continue
                else:
                    self.dig(surrounding_row, surrounding_col)

        # At some point, the dig will finish out the for loops, and so we'll want to return True when that's all done
        return True

    def flag_spot(self, row, col):
        self.board[row][col]['flagged'] = True
        return True

    def __str__(self):
        # This __str__ is a magic function where, if we call print() on this object, Board, print() will print out
        # whatever string we tell this function to return

        # So, let's make the board that we want the player to see!
        first_row = "   |"  # We're going to make a string of column numbers along the first row
        horizontal_line = "————"  # Make a string of dashes to underline the title column
        for r in range(self.dim_size):
            if len(str(r)) == 1:
                first_row += " " + str(r) + " |"
            elif len(str(r)) == 2:
                first_row += str(r) + " |"
            elif len(str(r)) == 3:
                first_row += str(r) + "|"
            horizontal_line += "————"

        board_values = [first_row, horizontal_line]
        # Now create a list of strings of row values for each row
        for r in range(self.dim_size):
            # Initialize string var that will hold all the values from each row in one string
            row_values = ""

            # Start each row with the row number
            if len(str(r)) == 1:
                row_values = str(r) + "  |"
            elif len(str(r)) == 2:
                row_values = str(r) + " |"
            elif len(str(r)) == 3:
                row_values = str(r) + "|"

            for c in range(self.dim_size):

                # if the spot hasn't been dug yet, we don't want the number showing
                if (r, c) not in self.dug:
                    # If the spot has been flagged, we want to show the flag symbol
                    if self.board[r][c]['flagged']:
                        row_values += self.symbols['flag'] + "|"
                    else:
                        row_values += self.symbols['undug spot'] + "|"

                # elif the spot was dug and it's a bomb, show the bomb symbol
                elif self.board[r][c]['is bomb']:
                    row_values += self.symbols['bomb'] + "|"

                # elif the spot was dug and it's a 0, show the 'no surrounding bombs' symbol
                elif self.board[r][c]['surrounding bombs'] == 0:
                    row_values += self.symbols['no surrounding bombs'] + "|"

                # otherwise, the spot was dug and it's not a bomb or a 0
                else:
                    row_values += " " + str(self.board[r][c]['surrounding bombs']) + " |"

            # Add each string of row values to the list of board values
            board_values += [row_values]
        # Put a horizontal line on the bottom for aesthetics
        board_values += [horizontal_line]

        # Since this function needs to return a string, we'll have to concatenate all of the 2D list rows
        # into one single string, using \n to break the lines
        string_board = "\n"
        for row in board_values:
            string_board += row + "\n"

        return string_board

    # --- Change Settings
    def general_settings(self):
        # Ask user what they want to change
        print(f"What would you like to change? You can enter something like '3' or 'Symbols' to edit game "
              f"settings, or enter 'quit' to quit the game."
              f"\n  1. Board dimensions (currently: {self.dim_size}x{self.dim_size})"
              f"\n  2. Number of bombs (currently: {self.num_bombs} bombs)"
              f"\n  3. Symbols (e.g. bomb symbol, flag symbol, etc.)"
              f"\n  4. Exit settings menu")
        # Check input is valid
        while True:
            user_input = input("> ")

            # If they want to change dimensions/bombs, just restart the game
            if user_input.lower().strip() in ["1", "board", "dimension", "dimensions", "dim", "board dimensions",
                                              "board dimension", "2", "bombs", "num", "number of bombs", "num bombs",
                                              "num of bombs"]:
                self.restart_game = True
                break
            # If they want to change symbols: change the symbols (be mindful of req. length)
            elif user_input.lower().strip() in ['3', 'symbols']:
                self.symbol_settings()
                break
            # If they want to exit, do so
            elif user_input.lower().strip() in ['4', 'exit', 'exit menu', 'exit settings', 'exit settings menu']:
                break
            elif user_input.lower().strip() in ['quit', 'quit game']:
                self.quit_game = True
                break
            else:
                print('Please enter a valid choice, such as "3" or "Symbols".')

    # This function gets user's input on what symbol they want to change and what they want the new symbol to be,
    # and it checks that the input is valid and that the 'new symbol' is not already in use
    def symbol_settings(self):
        # Set exit_settings variable so the function doesn't jump into change_symbol() if the user tried to exit
        exit_settings = False
        # Initialize variables to hold name of symbol that user wants to change & the new symbol that they want to use
        symbol_name, new_symbol = None, None

        print(f'What symbol would you like to change?'
              f'\n  1. Flag: "{self.symbols["flag"]}"'
              f'\n  2. Bomb: "{self.symbols["bomb"]}"'
              f'\n  3. Undug spot: "{self.symbols["undug spot"]}"'
              f'\n  4. Spot with no surrounding bombs: "{self.symbols["no surrounding bombs"]}"'
              f'\n  5. Exit settings menu')

        # Check input is valid & assign symbol_name
        while True:
            user_input = input('> ')

            if user_input.lower().strip() in ['1', 'flag', 'flag symbol', self.symbols["flag"]]:
                symbol_name = 'flag'
                break
            elif user_input.lower().strip() in ['2', 'bomb', 'bomb symbol', self.symbols["bomb"]]:
                symbol_name = 'bomb'
                break
            elif user_input.lower().strip() in ['3', 'undug', 'undug spot', 'undug symbol', 'undug spot symbol',
                                                self.symbols["undug spot"]]:
                symbol_name = 'undug spot'
                break
            elif user_input.lower().strip() in ['4', 'spot with no surrounding bombs', 'no surrounding bombs',
                                                'no bombs', self.symbols["no surrounding bombs"]]:
                symbol_name = 'no surrounding bombs'
                break
            elif user_input.lower().strip() in ['5', 'exit', 'exit menu', 'exit settings', 'exit settings menu']:
                exit_settings = True
                break
            elif user_input.lower().strip() in ['quit', 'quit game']:
                self.quit_game = True
                break
            else:
                print('Please enter a valid choice, such as "1" or "Flag".')

        # If user hasn't quit game or exited settings, ask for their new symbol
        if not self.quit_game and not exit_settings:
            print(f'The current "{symbol_name}" symbol is: "{self.symbols[symbol_name]}". What would you like the new '
                  f'symbol to be? The "{symbol_name}" symbol can be anywhere from 1-3 characters long.')

            # Check input is valid
            while True:
                new_symbol = input("> ")

                if new_symbol.lower().strip() in ['exit', 'exit menu', 'exit settings', 'exit settings menu']:
                    break
                elif new_symbol.lower().strip() in ['quit', 'quit game']:
                    self.quit_game = True
                    break
                # The actual symbol has to be len == 3, so check that len(input) <= 3, and then convert it to len == 3
                elif len(new_symbol) == 1:
                    new_symbol = " " + new_symbol + " "
                elif len(new_symbol) == 2:
                    new_symbol = new_symbol + " "
                elif len(new_symbol) == 3:
                    pass
                else:
                    print(f'Please enter a new symbol to use for the {symbol_name} that is 1-3 characters long. For '
                          f'example, "F" or "~~~".')
                    continue

                # Check that the new symbol is not already in use
                if new_symbol in self.symbols.values():
                    print('That symbol is already in use. Please enter a different symbol or enter "Exit" to exit '
                          'the settings menu.')
                    continue
                else:
                    self.change_symbol(symbol_name, new_symbol)
                    print(f'The {symbol_name} symbol has been changed to: "{new_symbol}"')
                    break

    # This function actually changes the symbol
    def change_symbol(self, symbol_name, new_symbol):
        self.symbols[symbol_name] = new_symbol


# play the game
def play():

    # This loop is so that if restart_game = True, the game will restart/jump back to the very top
    while True:
        # Set/reset restart_game so the game doesn't keep restarting accidentally
        restart_game = False

        print("\nWelcome to Minesweeper!"
              "\nInput 'quit' any time to quit the game.")

        # Initialize game_board, which will ask user for dimensions & number of bombs
        game_board = Board()

        # Set game's quit_game variable & check if the user quit during the creation of the board
        quit_game = game_board.quit_game

        # This loop makes each game go right into the next game with the same variables/settings until the player
        # quits or restarts (to change dim/bombs)
        while not quit_game:
            print("\n\n**************************"
                  "\n  **********************"
                  "\n         NEW GAME         "
                  "\n  **********************"
                  "\n**************************\n"
                  "\nInput 'settings' any time to change the game settings.")

            # Create a new board for this game
            game_board.make_new_board()

            safe = True  # Used to indicate whether the player is safe after they've dug a spot
            col = None
            row = None

            # as long as the number of spaces dug is less than the number of spaces available, keep playing this game
            while len(game_board.dug) < game_board.dim_size**2 - game_board.num_bombs:
                # First, show user the current board
                print(game_board)

                # Ask user where they want to dig and make sure the input is acceptable
                while not quit_game and not restart_game:
                    user_input = input("Where would you like to dig/flag? Input as col, row:\n> ")
                    try:
                        # Check if user asked to quit
                        if user_input.lower().strip() == "quit":
                            quit_game = True
                            continue

                        # Check if user wants to adjust settings
                        elif user_input.lower().strip() == 'settings':
                            game_board.general_settings()
                            # Adjust quit & restart values in case user quit during interface or wanted to change
                            # dimensions/number of bombs and game must restart
                            quit_game, restart_game = game_board.quit_game, game_board.restart_game

                            # After adjusting settings, loop back to asking user where they want to pl
                            continue

                        # Raise error if the user only inputs something like "1" or "1,", or if they don't put the comma
                        elif len(user_input) < 3 or "," not in user_input:
                            raise ValueError

                        # Split the input into two values to be assigned to col & row
                        # sometimes re.split has fluff in middle, so ensure you're taking the last value by using [-1]
                        user_input = re.split(',(\\s)*', user_input)
                        col, row = int(user_input[0]), int(user_input[-1])

                        # Throw up an error if the input is out of dimension range
                        if row < 0 or row >= game_board.dim_size or col < 0 or col >= game_board.dim_size:
                            raise ValueError

                        # If the user has already dug at that spot, ask them to pick a new spot
                        if (row, col) in game_board.dug:
                            print("Please pick a spot where you haven't dug yet.")
                            continue

                        break  # Can only get here if there are no errors and quit & restart are False

                    except ValueError:
                        print(f"Please enter 2 integers between 0 and {game_board.dim_size - 1} in col, row form "
                              f"(for example: 2, 3.), enter 'settings' to adjust game settings, or enter 'quit' to "
                              f"quit the game.")

                # Check that the user inputs D or F
                while not quit_game and not restart_game:
                    user_action = input(f"Would you like to dig (D) or flag (f) spot ({col}, {row})?\n> ")
                    if user_action.lower().strip() == "quit":
                        quit_game = True
                        continue
                    elif user_action.lower().strip() == 'settings':
                        game_board.general_settings()
                        # Adjust quit & restart values in case user quit during interface or wanted to change
                        # dim/no. of bombs and game must restart
                        quit_game, restart_game = game_board.quit_game, game_board.restart_game
                        continue

                    elif user_action.upper().strip() in ["F", "FLAG"]:
                        safe = game_board.flag_spot(row, col)
                        break
                    elif user_action.upper().strip() in ["D", "DIG"]:
                        safe = game_board.dig(row, col)
                        break
                    else:
                        print(f"Please enter 'D' to dig in spot ({col}, {row}), 'F' to flag that spot,"
                              f"'settings' to adjust game settings, or 'quit' to quit the game.")

                # quit, dug a bomb, or restarting to adjust variables, break out of this 'current game' loop
                if quit_game or not safe or restart_game:
                    break

            # 4 ways to end loop: ran out of space (safe!), dug a bomb (not so safe), quit game, restart to change vars
            if quit_game or restart_game:
                break
            elif safe:
                sleep(1)
                print("CONGRATULATIONS!!! YOU WON!!")
            else:
                sleep(1)
                print("Oof magoof. You died")

            # let's reveal the whole board
            sleep(1)
            game_board.dug = [(r, c) for r in range(game_board.dim_size) for c in range(game_board.dim_size)]
            print(game_board)
            sleep(1)

            # Reset the game_board values
            game_board.reset_board()

        if restart_game:
            continue
        else:  # Only other possibility is to have quit the game
            break

    # Can only get here by quitting the game
    print("Sorry to see you go!")


if __name__ == '__main__':
    play()
