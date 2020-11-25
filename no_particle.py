#!/usr/bin/env python3

"""
File Name:      my_agent.py
Authors:        Jeremy Webb
Date:           11/6/20

Description:    Python file for my agent.
Source:         Adapted from recon-chess (https://pypi.org/project/reconchess/)
"""



import random
from player import Player
from mcts import MCTS
import chess


# TODO: Rename this class to what you would like your bot to be named during the game.
class MyAgent(Player):

    def __init__(self):
        self.color = None
        self.current_board = None
        self.sense_request = -1
        
    def handle_game_start(self, color, board):
        """
        This function is called at the start of the game.

        :param color: chess.BLACK or chess.WHITE -- your color assignment for the game
        :param board: chess.Board -- initial board state
        :return:
        """

        self.color = color # set player color
        self.current_board = board # set the assumed board state
        pass
        
    def handle_opponent_move_result(self, captured_piece, captured_square):
        """
        This function is called at the start of your turn and gives you the chance to update your board.

        :param captured_piece: bool - true if your opponents captured your piece with their last move
        :param captured_square: chess.Square - position where your piece was captured
        """
        #TODO: Assume our opponents policy is random and update our board
        #TODO: If we have a piece captured, update the board with known piece position
        #TODO: Throw out any particles in which it wasn't possible for the opponent to move there
        print('\--------------Opponent Move--------------/')
        print(captured_piece)
        print(captured_square)
        if (captured_piece):
            self.current_board.turn = not self.color
            moves = list(self.current_board.pseudo_legal_moves)
            for move in moves.copy():
                if move.to_square != captured_square:
                    moves.remove(move)
            if len(moves) == 1:
                self.current_board.push(moves[0])
                self.sense_request = -1
            else:
                self.current_board.remove_piece_at(captured_square)
                self.sense_request = captured_square
        else:
            self.sense_request = -1

    def choose_sense(self, possible_sense, possible_moves, seconds_left):
        """
        This function is called to choose a square to perform a sense on.

        :param possible_sense: List(chess.SQUARES) -- list of squares to sense around
        :param possible_moves: List(chess.Moves) -- list of acceptable moves based on current board
        :param seconds_left: float -- seconds left in the game

        :return: chess.SQUARE -- the center of 3x3 section of the board you want to sense
        :example: choice = chess.A1
        """

        #TODO: Honestly not sure we might need some sort of policy to decide where to sense, or we can go random

        print('\--------------Choose Sense--------------/')
        sense_square = [0,0]
        if self.sense_request > -1:
            sense_square = [chess.square_file(self.sense_request), chess.square_rank(self.sense_request)]
            sense_square[0] = max(sense_square[0], 1)
            sense_square[1] = max(sense_square[1], 1)
            sense_square[0] = min(sense_square[0], 7)
            sense_square[1] = min(sense_square[1], 7)
        else:
            while (sense_square[0] == 0 or sense_square[0] == 7 or sense_square[1] == 0 or sense_square[1] == 7):
                temp = random.choice(possible_sense)
                sense_square = [chess.square_file(temp), chess.square_rank(temp)]
        
        self.sense_request = -1
        return chess.square(sense_square[0], sense_square[1])
        
    def handle_sense_result(self, sense_result):
        """
        This is a function called after your picked your 3x3 square to sense and gives you the chance to update your
        board.

        :param sense_result: A list of tuples, where each tuple contains a :class:`Square` in the sense, and if there
                             was a piece on the square, then the corresponding :class:`chess.Piece`, otherwise `None`.
        :example:
        [
            (A8, Piece(ROOK, BLACK)), (B8, Piece(KNIGHT, BLACK)), (C8, Piece(BISHOP, BLACK)),
            (A7, Piece(PAWN, BLACK)), (B7, Piece(PAWN, BLACK)), (C7, Piece(PAWN, BLACK)),
            (A6, None), (B6, None), (C8, None)
        ]
        """
        print('\--------------Handle Sense--------------/')
        print(sense_result)
        # TODO: Sense the board, update our current board with this sense
        # TODO: Fill in the rest of the board with guesses as to where the remaining unsensed enemy pieces are
        # Hint: until this method is implemented, any senses you make will be lost.
        sense_squares = [sense_result[i][0] for i in range(len(sense_result))]
        for square, piece in sense_result:
            if self.current_board.piece_at(square) == None or self.current_board.piece_at(square) == piece:
                continue
            self.current_board.turn = not self.color
            moves = list(self.current_board.pseudo_legal_moves)
            for square_to, piece_to in sense_result:
                if self.current_board.piece_at(square_to) != piece_to and self.current_board.piece_at(square) == piece_to and square != square_to:
                    move = chess.Move(square, square_to)
                    if move in moves and self.current_board.is_capture(move) != True:
                        self.current_board.push(move)
                        break
            if self.current_board.piece_at(square) == None or self.current_board.piece_at(square) == piece:
                continue
            self.current_board.turn = not self.color
            moves = list(self.current_board.pseudo_legal_moves)
            for move in moves:
                if move.from_square == square and move.to_square not in sense_squares and self.current_board.is_capture(move) != True:
                    self.current_board.push(move)
                    break
            if self.current_board.piece_at(square) == None or self.current_board.piece_at(square) == piece:
                continue
            rand_square = random.choice(chess.SQUARES)
            while rand_square in sense_squares or self.current_board.color_at(rand_square) != None:
                rand_square = random.choice(chess.SQUARES)
            self.current_board.set_piece_at(rand_square, self.current_board.remove_piece_at(square))
            
        for square, piece in sense_result:
            if self.current_board.piece_at(square) != None:
                continue
            self.current_board.turn = not self.color
            moves = list(self.current_board.pseudo_legal_moves)
            random.shuffle(moves)
            for move in moves:
                if move.to_square == square and self.current_board.piece_at(move.from_square) == piece and move.from_square not in sense_squares:
                    self.current_board.push(move)
                    break
                if move.to_square == square and move.promotion != None and move.promotion == piece.piece_type and move.from_square not in sense_squares:
                    self.current_board.push(move)
                    break
            if self.current_board.piece_at(square) == piece:
                continue
            random_squares = list(chess.SQUARES)
            random.shuffle(random_squares)
            for from_square in random_squares:
                if from_square in sense_squares:
                    continue
                if self.current_board.color_at(from_square) != (not self.color):
                    continue
                if piece.piece_type == self.current_board.piece_at(from_square).piece_type:
                    if piece.piece_type == chess.BISHOP:
                        from_type = (chess.square_rank(from_square) + chess.square_file(from_square)) % 2
                        to_type = (chess.square_rank(square) + chess.square_file(square)) % 2
                        if from_type != to_type:
                            continue
                    self.current_board.set_piece_at(square, self.current_board.remove_piece_at(from_square))
                    

        self.current_board.turn = self.color
        pass

    def choose_move(self, possible_moves, seconds_left):
        """
        Choose a move to enact from a list of possible moves.

        :param possible_moves: List(chess.Moves) -- list of acceptable moves based only on pieces
        :param seconds_left: float -- seconds left to make a move
        
        :return: chess.Move -- object that includes the square you're moving from to the square you're moving to
        :example: choice = chess.Move(chess.F2, chess.F4)
        
        :condition: If you intend to move a pawn for promotion other than Queen, please specify the promotion parameter
        :example: choice = chess.Move(chess.G7, chess.G8, promotion=chess.KNIGHT) *default is Queen
        """
        # TODO: update this method
        print('\--------------Choose Move--------------/')
        #print("Current board is:")
        self.current_board.turn = self.color
        print(self.current_board)
        #print(list(self.current_board.legal_moves))
        #print(possible_moves)
        search_tree = MCTS(10, self.color, self.current_board)
        search_tree.search()
        move = search_tree.pick_move()['move']
        # self.current_board.push(move)
        print(move)

        return move
        
    def handle_move_result(self, requested_move, taken_move, reason, captured_piece, captured_square):
        """
        This is a function called at the end of your turn/after your move was made and gives you the chance to update
        your board.

        :param requested_move: chess.Move -- the move you intended to make
        :param taken_move: chess.Move -- the move that was actually made
        :param reason: String -- description of the result from trying to make requested_move
        :param captured_piece: bool - true if you captured your opponents piece
        :param captured_square: chess.Square - position where you captured the piece
        """
        print('\--------------Handle Move--------------/')
        if taken_move != None:
            self.current_board.turn = self.color
            moves = list(self.current_board.pseudo_legal_moves)
            if taken_move in moves and self.current_board.is_capture(taken_move) == captured_piece:
                self.current_board.push(taken_move)
            elif taken_move in moves and self.current_board.is_capture(taken_move) != captured_piece:
                if captured_piece == True:
                    self.current_board.push(taken_move)
                else:
                    self.current_board.turn = not self.color
                    moves_opp = list(self.current_board.pseudo_legal_moves)
                    for move in moves_opp:
                        if move.from_square == taken_move.to_square:
                            board_temp = self.current_board.copy()
                            board_temp.push(move)
                            board_temp.turn = self.color
                            if taken_move in list(board_temp.pseudo_legal_moves) and board_temp.is_capture(taken_move) == False:
                                self.current_board = board_temp
                                break
                    self.current_board.turn = self.color
                    if self.current_board.is_capture(taken_move) != captured_piece:
                        rand_square = random.choice(chess.SQUARES)
                        while self.current_board.color_at(rand_square) != None:
                            rand_square = random.choice(chess.SQUARES)
                        self.current_board.set_piece_at(rand_square, self.current_board.remove_piece_at(taken_move.to_square))
                        self.current_board.push(taken_move)
            else:
                if self.current_board.color_at(taken_move.to_square) != None and captured_piece != True:
                    rand_square = random.choice(chess.SQUARES)
                    while self.current_board.color_at(rand_square) != None:
                        rand_square = random.choice(chess.SQUARES)
                    self.current_board.set_piece_at(rand_square, self.current_board.remove_piece_at(taken_move.to_square))
                self.current_board.set_piece_at(taken_move.to_square, self.current_board.remove_piece_at(taken_move.from_square))

        
    def handle_game_end(self, winner_color, win_reason):  # possible GameHistory object...
        """
        This function is called at the end of the game to declare a winner.

        :param winner_color: Chess.BLACK/chess.WHITE -- the winning color
        :param win_reason: String -- the reason for the game ending
        """
        # TODO: implement this method
        print('\--------------Game End--------------/')
        print(winner_color)
        print(win_reason)
        pass