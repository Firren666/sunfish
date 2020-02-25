# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 15:54:06 2020

@author: David Johansson
"""

import sunfish as sf

import os
import random
import time
import re
import chess
import chess.svg
import tools
from tools import renderFEN
from discord import File
from discord.ext import commands
from dotenv import load_dotenv
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')


class Game:
    PLAYER = 0
    ENGINE = 1
    
    def __init__(self):
        self.searcher = sf.Searcher()
        self.init()
        
    def togglePlayer(self):
        self.activePlayer = self.PLAYER if self.activePlayer == self.ENGINE else self.ENGINE
    
    def isMate(self):
        for move in tools.gen_legal_moves(self.hist[-1]):
            return False
        return True
    
    def move(self, move: str):
        # We query the user until she enters a (pseudo) legal move.
        
        match = re.match('([a-h][1-8])'*2, move)
        if match:
            move = sf.parse(match.group(1)), sf.parse(match.group(2))
        else:
            return False
        
        
        if move in self.hist[-1].gen_moves():
            self.hist.append(self.hist[-1].move(move))

            # After our move we rotate the board and print it again.
            # This allows us to see the effect of our move.
            self.togglePlayer()
            self.lastmove = match.group(1) + match.group(2)
            return self.lastmove
        return False
        
    def movesvg(self, move: str):
        self.move(move)
        return self.svg()
    
    def moveenginesvg(self):
        self.engine_move()
        return self.svg()
            
    def board(self):
        # if self.activePlayer == self.PLAYER:
        #     pos = self.hist[-1].rotate()
        # else:
        pos = self.hist[-1]
        uni_pieces = {'R':'♜', 'N':'♞', 'B':'♝', 'Q':'♛', 'K':'♚', 'P':'♟',
                      'r':'♖', 'n':'♘', 'b':'♗', 'q':'♕', 'k':'♔', 'p':'♙', '.':'·'}
        
        lboard = []
        for i, row in enumerate(pos.board.split()):
            srow = '  {} {}'.format(8-i, ' '.join(uni_pieces.get(p, p) for p in row))
            lboard.append(srow)
        lboard.append('    a b c d e f g h ')
        return '\n'.join(lboard)
    
    
    def svg(self):
        board = chess.Board(renderFEN(self.hist[-1]))
        lastmove = chess.Move.from_uci(self.lastmove) if self.lastmove else self.lastmove
        svg = chess.svg.board(board=board, lastmove=lastmove)
        return svg
    
    def save_svg(self, filename='chessboard.svg'):
        with open(filename, 'w') as f:
            f.write(self.svg())
            
    def png(self):
        self.save_svg()
        drawing = svg2rlg('chessboard.svg')
        renderPM.drawToFile(drawing, "chessboard.png", fmt="PNG")
        return "chessboard.png"
    
    def engine_move(self):
        # Fire up the engine to look for a move.
        start = time.time()
        for _depth, move, score in self.searcher.search(self.hist[-1], self.hist):
            if time.time() - start > 1:
                break
            
        self.lastmove = sf.render(119-move[0]) + sf.render(119-move[1])
        self.hist.append(self.hist[-1].move(move))
        self.togglePlayer()
        return self.lastmove
    
    def init(self):
        initial = (
            '         \n'
            '         \n'
            ' r.b.kb.r\n'
            ' ppp.ppp.\n'
            ' n.....p.\n'
            ' ..P..n..\n'
            ' ........\n'
            ' P.......\n'
            ' ....KP.P\n'
            ' ...q...q\n'
            '         \n'
            '         \n'
        )
        self.hist = [sf.Position(sf.initial, 0, (True,True), (True,True), 0, 0)]
        self.activePlayer = self.PLAYER
        self.lastmove = None
        
# def svg_to_png(svg):
#     img = cairo.ImageSurface(cairo.FORMAT_ARGB32, 400,400)
#     ctx = cairo.Context(img)
    
#     ## handle = rsvg.Handle(<svg filename>)
#     # or, for in memory SVG data:
#     handle = rsvg.Handle(None, str(svg))
#     handle.render_cairo(ctx)
    
#     return img.write_to_png("svg.png")

        
# @bot.command(name='99')
# async def nine_nine(ctx):
#     brooklyn_99_quotes = [
#         'I\'m the human form of the 💯 emoji.',
#         'Bingpot!',
#         (
#             'Cool. Cool cool cool cool cool cool cool, '
#             'no doubt no doubt no doubt no doubt.'
#         ),
#     ]

#     response = random.choice(brooklyn_99_quotes)
#     await ctx.send(response)
    
@bot.command(name='move', help='Enter a move like g8f6')
async def chess_move(ctx, move: str):
    if game.isMate():
        await ctx.send('Game is already over, the WINNER is {}'.format('Thor' if game.activePlayer else 'Active Player'))
    else:
        if game.move(move):
            if game.isMate():
                await ctx.send('Game is over, the WINNER is {}'.format('Thor' if game.activePlayer else 'Active Player'))
            else:
                game.engine_move()
                await ctx.send(file=File(game.png()))
                if game.isMate():
                    await ctx.send('Game is over, the WINNER is {}'.format('Thor' if game.activePlayer else 'Active Player'))
        else:
            await ctx.send('Illegal move! Please enter a move like g8f6')

@bot.command(name='restart', help='Restart chess game')
async def chess_restart(ctx):
    game.init()
    await ctx.send(file=File(game.png()))
    
@bot.command(name='play', help='Start chess game')
async def chess_start(ctx):
    game.init()
    await ctx.send(file=File(game.png()))
    
@bot.command(name='board', help='Print chessboard')
async def print_board(ctx):
    await ctx.send(file=File(game.png()))
    
if __name__ == '__main__':
    game = Game()
    bot.run(token)

    



# def main():
#     hist = [Position(initial, 0, (True,True), (True,True), 0, 0)]
#     searcher = Searcher()
#     while True:
#         print_pos(hist[-1])

#         if hist[-1].score <= -MATE_LOWER:
#             print("You lost")
#             break

#         # We query the user until she enters a (pseudo) legal move.
#         move = None
#         while move not in hist[-1].gen_moves():
#             match = re.match('([a-h][1-8])'*2, input('Your move: '))
#             if match:
#                 move = parse(match.group(1)), parse(match.group(2))
#             else:
#                 # Inform the user when invalid input (e.g. "help") is entered
#                 print("Please enter a move like g8f6")
#         hist.append(hist[-1].move(move))

#         # After our move we rotate the board and print it again.
#         # This allows us to see the effect of our move.
#         print_pos(hist[-1].rotate())

#         if hist[-1].score <= -MATE_LOWER:
#             print("You won")
#             break

#         # Fire up the engine to look for a move.
#         start = time.time()
#         for _depth, move, score in searcher.search(hist[-1], hist):
#             if time.time() - start > 1:
#                 break

#         if score == MATE_UPPER:
#             print("Checkmate!")

#         # The black player moves from a rotated position, so we have to
#         # 'back rotate' the move before printing it.
#         print("My move:", render(119-move[0]) + render(119-move[1]))
#         hist.append(hist[-1].move(move))



