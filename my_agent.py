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
        self.num_particles = 1000
        self.particles = []
        self.old_particles = []
        self.reset_turn = True
        self.my_moves = []
        self.moves_since_reset = 0
        
    def handle_game_start(self, color, board):
        """
        This function is called at the start of the game.

        :param color: chess.BLACK or chess.WHITE -- your color assignment for the game
        :param board: chess.Board -- initial board state
        :return:
        """

        self.color = color # set player color
        self.current_board = board # set the assumed board state
        
        # initialize particles to initial game state
        for i in range(self.num_particles):
            self.particles.append(board.copy())
        self.old_particles = self.particles.copy()
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
        new_particles = [] # initialize a new set of particles
        movesets = []
        # iterate through the known particles
        for board in self.particles:
            board.turn = not self.color # just in case

            # get all legal moves that the random player is given
            moves = list(board.generate_pseudo_legal_moves())

            # prune the moves list of moves that could not have happened
            movescopy = moves.copy()
            if (captured_piece == True): # if a piece was captured, remove all moves that don't capture it
                for move in moves:
                    if move.to_square != captured_square:
                        movescopy.remove(move)
            else: # if a piece was not captured, remove all moves that do
                for move in moves:
                    if board.is_capture(move):
                        movescopy.remove(move)
            
            if len(movescopy) == 0 and len(moves) != 0: # if there are no possible moves after pruning but there were options, toss out this particle
                continue

            moves = movescopy
            moves.append(chess.Move.null()) # add the possibility of no move since the agent does have this option
            
            # add the board and its corresponding moveset to the new set of particles
            new_particles.append(board)
            movesets.append(moves)

        # repopulate all removed particles back into the list of particles
        kept_num = len(new_particles)
        if (kept_num > 0):
            for i in range(self.num_particles - kept_num): # for every particle that was removed
                new_particles.append(new_particles[i % kept_num].copy()) # make a copy of a kept particle
                chosen = random.choice(movesets[i % kept_num]) # make a random move from its moveset
                counter = 0
                pseudo_legal = list(new_particles[-1].generate_pseudo_legal_moves())
                while (chosen not in pseudo_legal and counter < 50):
                    chosen = random.choice(movesets[i % kept_num])
                    counter += 1
                if counter >= 50:
                    new_particles[-1].push(chess.Move.null())
                    continue
                new_particles[-1].push(chosen)
            
            for i in range(kept_num): # for every particle that was kept
                chosen = random.choice(movesets[i]) # make a random move from its moveset
                counter = 0
                pseudo_legal = list(new_particles[i].generate_pseudo_legal_moves())
                while (chosen not in pseudo_legal and counter < 50):
                    chosen = random.choice(movesets[i])
                    counter += 1
                if counter >= 50:
                    new_particles[i].push(chess.Move.null())
                    continue
                new_particles[i].push(chosen)
    
        # reset new particle list if necessary
        new_particles = self._update_reset(new_particles, self.color, False)
        
        random.shuffle(new_particles) # randomize it to remove any sort of bias towards a specific board position
        self.particles = new_particles # update particles with the opponent move info
        self.current_board = self.particles[0] # since new_particles was just shuffled, this is effectively just a random sample
        self.current_board.turn = self.color

    def choose_sense(self, possible_sense, possible_moves, seconds_left):
        """
        This function is called to choose a square to perform a sense on.

        :param possible_sense: List(chess.SQUARES) -- list of squares to sense around
        :param possible_moves: List(chess.Moves) -- list of acceptable moves based on current board
        :param seconds_left: float -- seconds left in the game

        :return: chess.SQUARE -- the center of 3x3 section of the board you want to sense
        :example: choice = chess.A1
        """
        moves = list(self.current_board.legal_moves)
        our_pieces = []
        for move in moves:
            pos = str(move)[0:2]
            if pos not in our_pieces:
                our_pieces.append(pos)

        columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        piece_sence = []
        for piece in our_pieces:
            row = int(piece[1])
            col = 0
            for i in range(len(columns)):
                if piece[0] == columns[i]:
                    col = i
            index = (row-1)*8+col
            piece_sence.append(index)

        #need to remove edges of board for sense 
        smart_sence = possible_sense[8:-8]
        sides = []
        for sence in smart_sence:
            if sence % 8 == 0:
                sides.append(sence)
            if sence % 8 == 7:
                sides.append(sence)

        smart_sence = [i for i in smart_sence if i not in sides]

        avoid = []
        for spot in smart_sence:
            if spot in piece_sence:
                avoid.append(spot)

        if avoid:
            avg = sum(avoid)/len(avoid)
            sence = smart_sence[min(range(len(smart_sence)), key = lambda i: abs(smart_sence[i]-avg))]
        else:
            sence = random.choice(smart_sence)

        return sence

        
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

        new_particles = [] # initialize a new set of particles
        for board in self.particles: # iterate through each particle
            valid_board = True
            for square, piece in sense_result: # iterate through the sense result
                if board.piece_at(square) != piece: # check if the sense result and board are compatible
                    valid_board = False
                    break
            
            if valid_board == True: # only keep the particle if the sense result and board are compatible
                new_particles.append(board)
        
        # reset new particle list if necessary
        new_particles = self._update_reset(new_particles, self.color, True)

        # repopulate removed particles back into the list of particles
        kept_num = len(new_particles)
        for i in range(self.num_particles - kept_num):
            new_particles.append(new_particles[i % kept_num].copy())
        
        random.shuffle(new_particles) #randomize to remove bias
        self.particles = new_particles # update stored particles with sense info
        self.current_board = new_particles[0] # set the current board to a random particle
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
        #print(self.current_board)
        #print(list(self.current_board.legal_moves))
        #print(possible_moves)
        search_tree = MCTS(5, self.color, self.current_board)
        search_tree.search()
        move = search_tree.pick_move()['move']
        # self.current_board.push(move)

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
        # update particles with the move that was made
        new_particles = [] # initialize a new set of particles
        for board in self.particles: # iterate through current particles
            board.turn = self.color # just in case

            # if no move was made, then put the particle back
            if taken_move == None:
                board.push(chess.Move.null())
                new_particles.append(board)
                continue
            
            # if the move that was made wasn't possible in this board or making that move doesn't match up with
            # whether or not it's supposed to be a capture, throw this particle out
            if taken_move not in board.generate_pseudo_legal_moves() or captured_piece != board.is_capture(taken_move):
                continue
            
            # if it's a valid move, then update the board with the move and put it back
            board.push(taken_move)
            new_particles.append(board)
        
        # store the move that was taken for reset purposes
        self.my_moves.append(taken_move)
        # reset new particle list if necessary
        new_particles = self._update_reset(new_particles, not self.color, False)

        #repopulate pruned particles back into the main list
        kept_num = len(new_particles)
        for i in range(self.num_particles - kept_num):
            new_particles.append(new_particles[i % kept_num].copy())
        
        random.shuffle(new_particles) #randomize to remove bias
        self.particles = new_particles # update stored particles with sense info
        self.current_board = new_particles[0] # set the current board to a random particle
        self.current_board.turn = not self.color

        pass
        
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

    def _update_reset(self, new_particles, next_turn, sensing):   
        """
        This function checks if every single particle is objectively incorrect, and resets
        them if they are. Additionally, it keeps track of what the particles should be
        reset to.

        :param new_particles: a pruned list of particles that might be empty
        :param next_turn: what the next turn is (so that reset simulates the correct number of extra moves)
        :param sensing: boolean of whether or not we were sensing this turn. if not, we really don't know anything about the particles
        :returns new_particles: a pruned list of particles that is definitely not empty
        """
        kept_num = len(new_particles) # check the length of the pruned list
        if (kept_num > self.num_particles / 2): # if over half of the particles are decent, store them
            self.moves_since_reset += 1
            # make a copy of this pruned list and bring it up to the correct length
            self.old_particles = new_particles.copy()
            for i in range(self.num_particles - kept_num):
                self.old_particles.append(self.old_particles[i % kept_num])
            random.shuffle(self.old_particles)
            # re-initialize the reset variables since we have a new basis
            self.reset_turn = next_turn
            self.my_moves = []
        elif kept_num == 0: # if all particles are garbage, reset the
            self.moves_since_reset = 0
            new_particles = self.old_particles.copy() # set the particles to the last valid set

            # the last valid set of particles is out of date, so we need to simulate missed moves
            # if the next turn on the last stored reset was mine, make the first move in the my_moves array
            # if self.reset_turn == self.color and len(self.my_moves) > 0:
            #     for j in range(len(new_particles)):
            #         board = new_particles[j]
            #         board.turn = self.color
            #         if self.my_moves[0] not in list(board.generate_pseudo_legal_moves()):
            #             new_particles[j] = new_particles[j-1].copy()
            #             continue
            #         board.push(self.my_moves[0])
            #     del self.my_moves[0]

            # alternate opponent simulation and my moves until all of my stored moves have been applied
            for i in range(len(self.my_moves)): # for each time step
                for j in range (len(new_particles)): # for each particle
                    board = new_particles[j]
                    # randomly make a move for the opponent
                    board.turn = not self.color
                    moves = list(board.generate_pseudo_legal_moves())
                    moves.append(chess.Move.null())
                    temp = board.copy()
                    board.push(random.choice(moves))
                    counter = 0
                    while (self.my_moves[i] not in list(board.generate_pseudo_legal_moves()) and counter < 50):
                        board = temp.copy()
                        board.push(random.choice(moves))
                        counter += 1
                    if counter >= 50:
                        new_particles[j] = new_particles[j-1].copy()
                        continue
                    # we know exactly what the player's move was, so do that
                    board.push(self.my_moves[i])
                    new_particles[j] = board
            
            # if the next turn is my move, I need to simulate one extra opponent move
            # if next_turn == self.color:
            #     for j in range(len(new_particles)):
            #         board = new_particles[j]
            #         board.turn = not self.color
            #         moves = list(board.generate_pseudo_legal_moves())
            #         moves.append(chess.Move.null())
            #         board.push(random.choice(moves))
            #         new_particles[j] = board
        else:
            self.moves_since_reset += 1
        
        # return new_particles. Note: new_particles only changed if len was 0, otherwise it stayed constant
        return new_particles