import os
import random
import time

import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import textwrap

from google.generativeai import ChatSession


def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # we will use a single list to represent the 3x3 board
        self.current_winner = None  # keep track of winner!

    def print_board(self):
        for row in [self.board[i * 3:(i + 1) * 3] for i in range(3)]:
            print('| ' + ' | '.join(row) + ' |')

    def available_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def empty_squares(self):
        return ' ' in self.board

    def make_move(self, square, letter):
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def winner(self, square, letter):
        # check the row
        row_ind = square // 3
        row = self.board[row_ind * 3:(row_ind + 1) * 3]
        if all([spot == letter for spot in row]):
            return True
        # check the column
        col_ind = square % 3
        column = [self.board[col_ind + i * 3] for i in range(3)]
        if all([spot == letter for spot in column]):
            return True
        # check the diagonals
        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]  # left to right diagonal
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]  # right to left diagonal
            if all([spot == letter for spot in diagonal2]):
                return True
        # if all of these fail
        return False


def play(game, x_player, o_player, print_game=True):
    if print_game:
        game.print_board()

    letter = 'X'  # starting letter
    # iterate while the game still has empty squares
    while game.empty_squares():
        # get the move from the appropriate player
        if letter == 'O':
            square = o_player.get_move(game)
        else:
            square = x_player.get_move(game)
        # let's define a function to make a move!
        if game.make_move(square, letter):
            if print_game:
                print(letter + ' makes a move to square {}'.format(square + 1))  # Add 1 here
                game.print_board()
                print('')  # just empty line

            if game.current_winner:
                if print_game:
                    print(letter + ' wins!')
                if isinstance(x_player, AIPlayer):
                    message = f"{letter} wins!"
                    print(f"Message to AI: {message}")
                    response = x_player.chat.send_message(message)
                    print(f"AI response: {response.text}")
                if isinstance(o_player, AIPlayer):
                    message = f"{letter} wins!"
                    print(f"Message to AI: {message}")
                    response = o_player.chat.send_message(message)
                    print(f"AI response: {response.text}")
                return letter  # ends the loop and exits the game
            # after we made our move, we need to alternate letters
            letter = 'O' if letter == 'X' else 'X'  # switches player
            if isinstance(x_player, AIPlayer):
                x_player.inform_move(square)
            if isinstance(o_player, AIPlayer):
                o_player.inform_move(square)

        # tiny break to make things a little easier to read
        time.sleep(0.8)

    if print_game:
        print('It\'s a tie!')
        if isinstance(x_player, AIPlayer):
            message = "It's a tie!"
            print(f"Message to AI: {message}")
            response = x_player.chat.send_message(message)
            print(f"AI response: {response.text}")
        if isinstance(o_player, AIPlayer):
            message = "It's a tie!"
            print(f"Message to AI: {message}")
            response = o_player.chat.send_message(message)
            print(f"AI response: {response.text}")


class Player:
    def __init__(self, letter):
        self.letter = letter

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            square = input(self.letter + '\'s turn. Input move (1-9): ')
            try:
                val = int(square) - 1  # Subtract 1 here
                if val not in game.available_moves():
                    raise ValueError
                valid_square = True
            except ValueError:
                print('Invalid square. Try again.')
        return val


class AIPlayer(Player):
    def __init__(self, letter, chat):
        super().__init__(letter)
        self.chat = chat
        message = "We're going to play Tic Tac Toe. You're '{}'. I'll tell you the position I put on the " \
                  "board. Please reply with your move as a digit from 1-9 only.".format(letter)
        print(f"Message to AI: {message}")
        response = self.chat.send_message(message)
        print(f"AI response: {response.text}")

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            message = f"{self.letter}'s turn. Please answer with a digit from 1-9 only."
            print(f"Message to AI: {message}")
            response = self.chat.send_message(message)
            square = response.text
            print(f"AI response: {square}")
            try:
                val = int(square) - 1  # Subtract 1 here
                if val not in game.available_moves():
                    raise ValueError
                valid_square = True
            except ValueError:
                print('Invalid square. Try again.')
        return val

    def inform_move(self, move):
        message = f"I put my '{self.letter}' on position {move + 1}."
        print(f"Message to AI: {message}")
        self.chat.send_message(message)


if __name__ == '__main__':
    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
    chat = model.start_chat()

    x_player = Player('X')
    o_player = AIPlayer('O', chat)
    game = TicTacToe()
    play(game, x_player, o_player, print_game=True)
