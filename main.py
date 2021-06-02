import random
import re
from time import sleep


class Board:
    def __init__(self, dim_size, num_bombs):
        self.dim_size = dim_size
        self.num_bombs = num_bombs

        # Create the board
        # We'll use a helper function to make the board ('make_new_board()')
        self.bomb_symbol = "X"  # Must be len 1
        self.undug_spot_symbol = " - "  # Must be len 3 for __str__ function stuff
        self.dug_spot_0_value_symbol = "   "  # Must be len 3 for __str__ function stuff
        self.flagged_spot_symbol = " • "  # ?? Might have to be len 1 (check after finished editing Flagging ability
        self.board = self.make_new_board()  # Makes new board & plants bombs
        self.assign_values_to_board()

        # Initialize a set to keep track of which locations have been dug (row, col) tuples
        self.dug = set()  # if we dig at 0,0, then self.dug = {(0,0)}

    def make_new_board(self):
        # Construct a new board based on the dim size & num bombs
        # We should construct the list of lists here (or whatever representation you prefer,
        #   but since we have a 2D board, list of lists is more natural))

        # Each value is a 2-element list where 1st value, 'None', will be the bomb symbol or number of
        # surrounding bombs, and the next value, False is to track whether the spot has been flagged
        board = [[[None, False] for i in range(self.dim_size)] for j in range(self.dim_size)]

        # Plant bombs
        bombs_planted = 0
        while bombs_planted < self.num_bombs:
            spot = random.randint(0, self.dim_size**2 - 1)
            row = spot // self.dim_size
            col = spot % self.dim_size

            if board[row][col][0] == self.bomb_symbol:
                continue
            board[row][col][0] = self.bomb_symbol
            bombs_planted += 1

        return board

    def assign_values_to_board(self):

        # Go through each spot on the board
        for r in range(self.dim_size):
            for c in range(self.dim_size):

                # If spot contains a bomb, skip over it (don't want to overwrite bomb value)
                if self.board[r][c][0] == self.bomb_symbol:
                    continue

                # Otherwise, assign the value of the num of surrounding bombs
                self.board[r][c][0] = self.get_num_surrounding_bombs(r, c)

    def get_num_surrounding_bombs(self, row, col):
        # Initialize counter for number of bombs
        bomb_count = 0

        # For each of the 8 squares around that spot, if there's a bomb, increment counter by +1
        # We don't want the counter to go below 0 or above dim size (since range will go up to dim size - 1)
        for surrounding_row in range(max(0, row-1), min(self.dim_size, (row+1)+1)):
            for surrounding_col in range(max(0, col-1), min(self.dim_size, (col+1)+1)):

                # We don't want to count the spot itself--just its surrounding spots
                if surrounding_row == row and surrounding_col == col:
                    continue
                if self.board[surrounding_row][surrounding_col][0] == self.bomb_symbol:
                    bomb_count += 1

        return bomb_count

    def dig(self, row, col):
        # First, let's add this spot to our set of dug places as a tuple
        self.dug.add((row, col))

        # Then we have 3 scenarios:
        # 1) There's a bomb where we dig => return False
        if self.board[row][col][0] == self.bomb_symbol:
            return False
        # 2) We dig a spot that's next to a bomb => we stop digging
        elif self.board[row][col][0] > 0:
            return True

        # 3) We dig a spot that's not next to a bomb and must keep digging
        # To decide how to keep digging, we'll use the same pattern we used for checking for bombs
        # However, we'll use recursion to dig up a bunch of spots since we're doing the same thing over and over
        for surrounding_row in range(max(0, row-1), min(self.dim_size, (row+1)+1)):
            for surrounding_col in range(max(0, col-1), min(self.dim_size, (col+1)+1)):
                if (surrounding_row, surrounding_col) in self.dug:  # If we hit a spot we've already dug, jump over it
                    continue
                else:
                    self.dig(surrounding_row, surrounding_col)

        # At some point, the dig will finish out the for loops, and so we'll want to return True when that's all done
        return True

    def flag_spot(self, row, col):
        self.board[row][col][1] = True
        return True

    def __str__(self):
        # This __str__ is a magic function where, if we call print() on this object, Board, print() will print out
        # whatever string we tell this function to return

        # So, let's make the board that we want the player to see!
        first_row = "   |"  # Make a string of column numbers for the first row
        horizontal_line = "----"  # Make a string of dashes to underline the title column for the second row
        for r in range(self.dim_size):
            if len(str(r)) == 1:
                first_row += " " + str(r) + " |"
            elif len(str(r)) == 2:
                first_row += str(r) + " |"
            elif len(str(r)) == 3:
                first_row += str(r) + "|"
            horizontal_line += "----"

        board_values = [first_row, horizontal_line]
        # Now create a list of strings of row values for each row
        for r in range(self.dim_size):
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
                    if self.board[r][c][1]:
                        row_values += self.flagged_spot_symbol + "|"
                    else:
                        row_values += self.undug_spot_symbol + "|"

                # if the spot was dug and it's a 0, show dug_spot_0_value_symbol
                elif self.board[r][c][0] == 0:
                    row_values += self.dug_spot_0_value_symbol + "|"
                else:  # The spot has been dug and it's not a 0
                    row_values += " " + str(self.board[r][c][0]) + " |"  # Concat all values from each row
            board_values += [row_values]  # Then separate the values w/ column lines
        board_values += [horizontal_line]

        # Since this function needs to return a string, we'll have to concatenate all of the 2D list rows
        # into one single string, using \n to break the lines
        string_board = "\n"
        for row in board_values:
            string_board += row + "\n"

        return string_board


def get_game_variables():
    print("\nWelcome to Minesweeper!\nInput 'quit' any time to quit the game.")
    quit_game = False
    dim = None
    bombs = None

    # Get int number for dimension size
    sleep(0.5)
    print("\nWhat size square board would you like to play on? (e.g. enter '10' for a 10x10 board).")
    while not quit_game:
        dimension_input = input("> ")
        try:
            # Check if user wants to quit
            if dimension_input.lower() == "quit":
                quit_game = True
                break

            # Otherwise, check that the input is a valid dimension size
            dim = int(dimension_input)
            if dim <= 0:  # Dim needs to be greater than 0
                raise ValueError
            break
        except ValueError:
            print("Please enter an integer that is greater than 0.")

    # Get int number for bombs
    sleep(0.5)
    while not quit_game:
        bombs_input = input("And how many bombs would you like to have on your board?\n> ")
        try:
            # Check if user wants to quit
            if bombs_input.lower() == "quit":
                quit_game = True
                break

            # Otherwise, check that bomb input is valid integer
            bombs = int(bombs_input)
            if bombs <= 0 or bombs >= dim**2:
                raise ValueError
            break
        except ValueError:
            print(f"Please enter an integer that is greater than 0 but less than {dim**2}.")

    return [dim, bombs, quit_game]


# play the game
def play():
    # Step 1: create the board & plant bombs
    variables = get_game_variables()
    quit_game = variables[2]

    while not quit_game:

        # Step 2: show the user the board and ask for where they want to dig
        # Step 3a: if location is a bomb, show GAME OVER message
        # Step 3b: if location not a bomb, dig recursively until each square is at least
        #   next to a bomb
        # Step 4: repeat steps 2 and 31/b until there are no more places to dig -> VICTORY!

        print("\n\n**************************\n  **********************\n         NEW GAME         \n  **********************\n**************************\n\n")
        dim_size, num_bombs = variables[0], variables[1]
        game_board = Board(dim_size, num_bombs)
        safe = True
        col = None
        row = None
        # as long as the number of spaces dug is less than the number of spaces available, keep playing
        while len(game_board.dug) < dim_size**2 - num_bombs:
            print(game_board)

            # Make sure user input is acceptable
            while not quit_game:
                user_input = input("Where would you like to dig/flag? Input as col, row:\n> ")
                try:
                    if user_input.lower() == "quit":
                        quit_game = True
                        break

                    # Throw up an error if the user only inputs something like "1" or "1,", or if they don't put the comma
                    if len(user_input) < 3 or "," not in user_input:
                        raise ValueError

                    # Split the input into two values to be assigned to col & row
                    # sometimes re.split has some fluff in middle, so you ensure you're taking the last value by using [-1]
                    user_input = re.split(',(\\s)*', user_input)
                    col, row = int(user_input[0]), int(user_input[-1])

                    # Throw up an error if the input is out of dimension range
                    if row < 0 or row >= dim_size or col < 0 or col >= dim_size:
                        raise ValueError

                    # If the user has already dug at that spot, ask them to pick a new spot
                    if (row, col) in game_board.dug:
                        print("Please pick a spot where you haven't dug yet.")
                        continue
                    break
                except ValueError:
                    print(f"Please type 2 integers between {0} and {dim_size - 1} in col, row form. For example:   2, 3.")

            # Check that the user inputs D or F
            while not quit_game:
                user_action = input(f"Would you like to dig (D) or flag (f) spot ({col}, {row})?\n> ")
                if user_action.lower() == "quit":
                    quit_game = True
                    break
                elif user_action.upper() in ["F", "FLAG"]:
                    safe = game_board.flag_spot(row, col)
                    break
                elif user_action.upper() in ["D", "DIG"]:
                    safe = game_board.dig(row, col)
                    break
                else:
                    print(f"Please enter 'D' to dig in spot ({col}, {row}) or 'F' to flag that spot.")

            if quit_game or not safe:  # quit or dug a bomb
                break

        # 3 ways to end loop: ran out of space (safe!), dug a bomb (not so safe), quit game
        if quit_game:
            break
        elif safe:
            sleep(1)
            print("CONGRATULATIONS!!! YOU WON!!")
        else:
            sleep(1)
            print("Oof magoof. You ded")

        # let's reveal the whole board
        sleep(1)
        game_board.dug = [(r, c) for r in range(dim_size) for c in range(dim_size)]
        print(game_board)
        sleep(1)

    # Can only get here by quitting the game
    print("Sorry to see you go!")


if __name__ == '__main__':
    play()
