import random
import re
import sys
from time import sleep

# This list of acceptable quit responses needs to be accessible globally
quit_responses = ['quit', 'quit game']


# This quit_game() function needs to be accessible globally
def quit_game():
    print("Sorry to see you go!")
    sys.exit()


class Board:
    def __init__(self):
        # restart_game variable will be set to True if user wants to edit dim/no. of bombs during the game
        self.restart_game = False

        # Initialize dimension & number of bombs to None and we'll run set_dim_size() and set_num_bombs() at the top of
        # the restart loop so user can adjust dim/bombs without completely resetting any symbol changes
        self.dim_size = None
        self.num_bombs = None

        # Set game symbols. All symbols must be len 3 for __str__ function printing.
        # 'no surrounding bombs' is the symbol that prints when a spot is dug up but there aren't any surrounding bombs.
        # You could also just print the spot's 'bombs' value like you would for any other spot--which would be 0--but
        # you'll have to edit __str__ if you want 0 spots to print 0 instead of the 'no surrounding bombs' symbol.
        self.symbols = {'bomb': ' X ', 'undug spot': ' - ', 'no surrounding bombs': '   ', 'flag': ' • '}

        # Initialize board to None and we'll run Board.make_new_board() at the top of each game so a new board is
        # created each time.
        self.board = None

        # Initialize a set to keep track of which locations have been dug using (row, col) tuples.
        # I didn't set 'is dug' as one of the keys in each 'spot' because the game needs to be able to compare the
        # length of Board.dug to (board size - num. bombs) to check if the player has dug up all of the safe spots.
        self.dug = set()  # if we dig at 0,0, then self.dug = {(0,0)}

    def set_dim_size(self):
        print("\nWhat size square board would you like to play on? (e.g. enter '10' for a 10x10 board).")
        while True:
            dimension_input = input("> ").lower().strip()
            try:
                # Check if user wants to quit
                if dimension_input in quit_responses:
                    quit_game()

                # Otherwise, check that the input is a valid dimension size
                dim = int(dimension_input)
                if dim <= 0:  # Dim needs to be greater than 0
                    raise ValueError

                # If no errors are raised, set board dim_size dim
                self.dim_size = dim
                break

            except ValueError:
                print("Please enter an integer that is greater than 0 and less than 1000.")

    def set_num_bombs(self):
        # Level suggestions: Easy: 10-15% of the board is bombs, Med: 15-25%, Hard: 25-35%
        print(f"\nHow many bombs would you like to have on your board?"
              f"\n  For an easy game, I'd suggest: "
              f"{(self.dim_size ** 2) * 1 // 10} - {(self.dim_size ** 2) * 15 // 100} bombs."
              f"\n  For a medium game, I'd suggest: "
              f"{((self.dim_size ** 2) * 15 // 100) + 1} - {(self.dim_size ** 2) * 25 // 100} bombs."
              f"\n  For a hard game, I'd suggest: "
              f"{((self.dim_size ** 2) * 25 // 100) + 1} - {(self.dim_size ** 2) * 35 // 100} bombs.")
        while True:
            bombs_input = input("> ").lower().strip()
            try:
                # Check if user wants to quit
                if bombs_input in quit_responses:
                    quit_game()

                # Otherwise, check that bomb input is a valid integer
                bombs = int(bombs_input)
                if bombs <= 0 or bombs >= self.dim_size ** 2:
                    raise ValueError

                # If no errors are raised, return the number of bombs
                self.num_bombs = bombs
                break

            except ValueError:
                print(f"Please enter an integer that is greater than 0 but less than {self.dim_size ** 2}.")

    # Call this function at the start of each game to create a new board
    def make_new_board(self):
        # Construct a new board based on the dim size & num bombs.
        # We should construct a list of lists here (or whatever representation you prefer, but since we have a 2D
        # board, list of lists is more natural).

        # Each element in the innermost list (so, each 'spot') is a 3-element dictionary where 'is bomb' tracks whether
        # the spot is a bomb, 'surrounding bombs' holds the number of surrounding bombs (if spot isn't a bomb), and
        # 'flagged' tracks whether the spot has been flagged or not.
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
        # Now assign values to each spot on the board
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

        # For each of the 8 squares around that spot, if there's a bomb, increment counter by +1.
        # We don't want the range to go below 0 or above dim size (since range will go up to dim size - 1).
        for surrounding_row in range(max(0, row - 1), min(self.dim_size, (row + 1) + 1)):
            for surrounding_col in range(max(0, col - 1), min(self.dim_size, (col + 1) + 1)):

                # We don't want to count the spot itself--just its surrounding spots
                if surrounding_row == row and surrounding_col == col:
                    continue
                if self.board[surrounding_row][surrounding_col]['is bomb']:
                    bomb_count += 1

        return bomb_count

    def dig_spot(self, row, col):
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
                    self.dig_spot(surrounding_row, surrounding_col)

        # At some point, the dig will finish out the for loops, and so we'll want to return True when that's all done
        return True

    def flag_spot(self, row, col):
        self.board[row][col]['flagged'] = True
        return True

    def __str__(self):
        # Let's make the board that we want the player to see!
        first_row = "   |"  # We're going to make a string of column numbers along the first row
        horizontal_line = "————"  # Make a string of dashes to underline the title column

        for c in range(self.dim_size):
            # Concat each column number + "|" divider onto the first_row string. Note that numbers may have dif lengths
            if len(str(c)) == 1:  # Center-align col numbers that are of length 1
                first_row += " " + str(c) + " |"
            elif len(str(c)) == 2:  # Left-align col numbers that are of length 2
                first_row += str(c) + " |"
            elif len(str(c)) == 3:
                first_row += str(c) + "|"

            # For each additional column, we also want to extend the horizontal line
            horizontal_line += "————"

        # Initialize the list that'll hold all of the strings that represent each row of the board
        board_values = [first_row, horizontal_line]
        # Now create a list of strings of row values for each row
        for r in range(self.dim_size):
            # Initialize string var that will hold all the values from each row in one string
            row_values = ""

            # Start each row with the row number.
            # Again, be mindful that '3' and '124' would take up diff amounts of space
            if len(str(r)) == 1:  # Center-align row numbers that are of length 1
                row_values = str(r) + "  |"
            elif len(str(r)) == 2:  # Left-align row numbers that are of length 2
                row_values = str(r) + " |"
            elif len(str(r)) == 3:
                row_values = str(r) + "|"

            # Now add the values of each spot in that row onto the row_values string
            for c in range(self.dim_size):

                # If the spot hasn't been dug yet, we don't want its value showing
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

                # otherwise, the spot was dug and it's not a bomb or a 0 (it has a non-zero 'surrounding bombs' value)
                else:
                    row_values += " " + str(self.board[r][c]['surrounding bombs']) + " |"

            # Add that string of row values to the list of board values
            board_values += [row_values]

        # Put a horizontal line at the very bottom of the board for aesthetics
        board_values += [horizontal_line]

        # Since this function needs to return a string, we'll have to concatenate all of the row_values in the list
        # into one single string, using \n to break the lines
        string_board = "\n"
        for row in board_values:
            string_board += row + "\n"

        return string_board

    # --- Change Settings
    def general_settings(self):
        # Ask user what setting they want to change
        print(f"\nWhat would you like to change? You can enter something like '3' or 'Symbols' to edit game "
              f"settings, or enter 'quit' to quit the game."
              f"\n  1. Board dimensions or number of bombs "
              f"(currently a {self.dim_size}x{self.dim_size} board with {self.num_bombs} bombs)"
              f"\n  2. Symbols (e.g. bomb symbol, flag symbol, etc.)"
              f"\n  3. Exit settings menu")
        # Check input is valid
        while True:
            user_input = input("> ").lower().strip()

            # If user wants to change dimensions/bombs, just restart the game
            if user_input in ["1", "board", "dimension", "dimensions", "dim", "board dimensions", "board dim",
                              "board dims", "board dimension", "board and bombs", "dim and bombs", "dim & bombs",
                              "board & bombs", "bombs", "num", "number of bombs", "num bombs", "num of bombs"]:
                self.restart_game = True
                break
            # If they want to change symbols, move into symbol_settings()
            elif user_input in ['2', 'symbols', 'sym', 'symbol', 'syms', 'symbs', 'symb']:
                self.symbol_settings()
                break
            # If user wants to exit or quit, do so
            elif user_input in ['3', 'exit', 'exit menu', 'exit settings', 'exit settings menu']:
                break
            elif user_input in quit_responses:
                quit_game()
            else:
                print('Please enter a valid choice, such as "3" or "Symbols".')

        # Unless the user is restarting the game, print the board after settings have been adjust/after they exit so
        # that when the game loops back to asking where they want to play/if they want to dig or flag, they can easily
        # reference the board
        if not self.restart_game:
            sleep(0.5)
            print(self)

    # This function gets user's input on what symbol they want to change and what they want the new symbol to be,
    # and it checks that the input is valid and that the 'new symbol' is not already in use
    def symbol_settings(self):
        # Set exit_settings variable so the function doesn't execute change_symbol() if the user tries to exit
        exit_settings = False
        # Initialize variables to hold name of symbol that user wants to change & the new symbol that they want to use
        symbol_name, new_symbol = None, None

        print(f'\nWhat symbol would you like to change?'
              f'\n  1. Flag: "{self.symbols["flag"]}"'
              f'\n  2. Bomb: "{self.symbols["bomb"]}"'
              f'\n  3. Undug spot: "{self.symbols["undug spot"]}"'
              f'\n  4. Spot with no surrounding bombs: "{self.symbols["no surrounding bombs"]}"'
              f'\n  5. Exit settings menu')

        # Check option selection input is valid & assign symbol_name
        while True:
            user_input = input('> ').lower().strip()

            # Let user input the actual symbol to identify the symbol name, as long as
            # self.symbols[symbol].lower().strip() != '', b/c the function would accept the user accidentally pressing
            # enter.
            # So, if self.symbols[symbol].lower().strip() == '', don't include it in the list of acceptable responses.
            if user_input in ['1', 'flag', 'flag symbol',
                              self.symbols["flag"].lower().strip() if self.symbols["flag"].lower().strip() != '' else None]:
                symbol_name = 'flag'
                break
            elif user_input in ['2', 'bomb', 'bomb symbol',
                                self.symbols["bomb"].lower().strip() if self.symbols["bomb"].lower().strip() != '' else None]:
                symbol_name = 'bomb'
                break
            elif user_input in ['3', 'undug', 'undug spot', 'undug symbol', 'undug spot symbol',
                                self.symbols["undug spot"].lower().strip() if self.symbols["undug spot"].lower().strip() != '' else None]:
                symbol_name = 'undug spot'
                break
            elif user_input in ['4', 'spot with no surrounding bombs', 'no surrounding bombs', 'no bombs',
                                self.symbols["no surrounding bombs"].lower().strip() if self.symbols["no surrounding bombs"].lower().strip() != '' else None]:
                symbol_name = 'no surrounding bombs'
                break
            elif user_input in ['5', 'exit', 'exit menu', 'exit settings', 'exit settings menu']:
                exit_settings = True
                break
            elif user_input in quit_responses:
                quit_game()
            else:
                print('Please enter a valid choice, such as "1" or "Flag".')

        # If user hasn't exited settings, ask for their new symbol
        if not exit_settings:
            print(f'\nThe current "{symbol_name}" symbol is: "{self.symbols[symbol_name]}". What would you like the '
                  f'new symbol to be? The new symbol can be anywhere from 1-3 characters long.')

            # Check new symbol input is valid
            while True:
                new_symbol = input("> ")  # Don't want to lower().strip() input bc user might want to use spaces

                if new_symbol.lower().strip() in ['exit', 'exit menu', 'exit settings', 'exit settings menu']:
                    break
                elif new_symbol.lower().strip() in quit_responses:
                    quit_game()
                # The actual symbol has to be len == 3, so check that len(input) <= 3, and then convert it to len == 3
                elif len(new_symbol) == 1:  # Center-align symbols of len 1
                    new_symbol = " " + new_symbol + " "
                elif len(new_symbol) == 2:  # Left-align symbols of len 2
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
                    print(f'\nThe {symbol_name} symbol has been changed to: "{new_symbol}"')
                    break

    # This function actually changes the symbol
    def change_symbol(self, symbol_name, new_symbol):
        self.symbols[symbol_name] = new_symbol

    # Call this function at end of each game to reset board values so they can be created anew when the next game starts
    def reset_board(self):
        self.restart_game = False
        self.board = None
        self.dug = set()


# play the game
def play():
    # Initialize game_board
    game_board = Board()

    print("\nWelcome to Minesweeper!"
          "\nInput 'quit' any time to quit the game.")

    # Create lists of responses that need to be used multiple times in this function
    settings_responses = ['settings', 'setting', 'set']

    # This loop is so that if Board.restart_game = True, the game will restart/jump back to the very top
    while True:
        # Set board dimensions & number of bombs
        game_board.set_dim_size()
        game_board.set_num_bombs()

        # This loop makes each game go right into the next game with the same dimensions & no. of bombs
        while True:

            sleep(0.5)
            print("\n\n**************************"
                  "\n  **********************"
                  "\n         NEW GAME         "
                  "\n  **********************"
                  "\n**************************\n")
            sleep(0.5)

            print("Input 'settings' any time to change the game settings.")
            sleep(0.5)

            # Create a new board for this game
            game_board.make_new_board()

            safe = True  # Used to indicate whether the player is safe after they've dug a spot
            col, row = None, None

            # as long as the number of spaces dug is less than the number of spaces available, keep playing this game
            while len(game_board.dug) < game_board.dim_size**2 - game_board.num_bombs:
                # First, show user the current board
                sleep(0.5)
                print(game_board)

                # Ask user where they want to dig and make sure the input is acceptable
                while not game_board.restart_game:
                    # Don't need \n at the start of this message b/c the printed game board has an extra \n underneath
                    user_input = input("Where would you like to dig/flag? Input as col, row:\n> ").lower().strip()
                    try:
                        # If user asked to quit, quit
                        if user_input in quit_responses:
                            quit_game()
                        # Elif user wants to adjust settings, open up the settings
                        elif user_input in settings_responses:
                            game_board.general_settings()
                            # After adjusting settings, loop back to asking user where they want to play.
                            # If Board.restart_game was set to True during settings, the game will break out of loop
                            continue
                        # Elif user only inputs something like "1" or "1,", or if they don't put the comma, raise error
                        elif len(user_input) < 3 or "," not in user_input:
                            raise ValueError

                        # Split the input into two values to be assigned to col & row.
                        # sometimes re.split has fluff in middle, so ensure you're taking the last value by using [-1].
                        user_input = re.split(',(\\s)*', user_input)
                        col, row = int(user_input[0]), int(user_input[-1])

                        # Throw up an error if the input is out of dimension range
                        if row < 0 or row >= game_board.dim_size or col < 0 or col >= game_board.dim_size:
                            raise ValueError

                        # If the user has already dug at that spot, ask them to pick a new spot
                        if (row, col) in game_board.dug:
                            print("Please pick a spot where you haven't dug yet.")
                            continue

                        break  # Can only get here if there are no errors and Board.restart_game is False

                    except ValueError:
                        print(f"Please enter 2 integers between 0 and {game_board.dim_size - 1} in col, row form "
                              f"(for example: 2, 3.), enter 'settings' to adjust game settings, or enter 'quit' to "
                              f"quit the game.")

                # Check that user inputs D or F
                while not game_board.restart_game:
                    print(f"\nWould you like to dig (D) or flag (F) spot ({col}, {row})?")
                    user_action = input("> ").lower().strip()

                    if user_action in quit_responses:
                        quit_game()
                    elif user_action in settings_responses:
                        game_board.general_settings()
                        # After adjusting settings, loop back to asking user whether they want to dig or flag.
                        # If Board.restart_game was set to True during settings, the game will break out of loop.
                        continue
                    elif user_action in ["f", "flag"]:
                        safe = game_board.flag_spot(row, col)
                        break
                    elif user_action in ["d", "dig"]:
                        safe = game_board.dig_spot(row, col)
                        break
                    else:
                        print(f"Please enter 'D' to dig in spot ({col}, {row}), 'F' to flag that spot,"
                              f"'settings' to adjust game settings, or 'quit' to quit the game.")

                # If user dug a bomb or is restarting game to adjust variables, break out of this current game loop
                if not safe or game_board.restart_game:
                    break

            # 3 ways to end loop: restarting game to change dim/bombs, ran out of space (safe!), dug a bomb (not safe)
            if game_board.restart_game:
                game_board.reset_board()
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

            # Reset the game_board values before jumping into the next game
            game_board.reset_board()


if __name__ == '__main__':
    play()
