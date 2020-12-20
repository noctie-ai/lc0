import sys
from backends import Weights, Backend, GameState
import matplotlib.pyplot as plt
import numpy as np
import time
import random
import chess
import chess.pgn
import os

path = os.path.dirname(os.path.abspath(__file__))

#w = Weights("./384x30-t60-4300.pb.gz")
w = Weights(path + "/128x10-t60-2-5300.pb.gz")

w1100 = Weights(path + "/1000-1200-scratch-swa-36000.pb.gz")
w1450 = Weights(path + "/1400-1500-scratch-swa-60000.pb.gz")
w1750 = Weights(path + "/1700-1800-scratch-swa-60000.pb.gz")
w2150 = Weights(path + "/2000-2100-scratch-swa-60000.pb.gz")

start_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
back = Backend(weights=w)
b1100 = Backend(weights=w1100)
b1450 = Backend(weights=w1450)
b1750 = Backend(weights=w1750)
b2150 = Backend(weights=w2150)


board = chess.Board()
fen = board.fen()
start_fen = fen

pgn = open("game8.pgn")
game = chess.pgn.read_game(pgn)

names = ["1100", "1450", "1750", "2150", "128x10"]
board = game.board()

prob1 = {}
prob1["1100"] = 1.0
prob1["1450"] = 1.0
prob1["1750"] = 1.0
prob1["2150"] = 1.0
prob1["128x10"] = 1.0

prob2 = {}
prob2["1100"] = 1.0
prob2["1450"] = 1.0
prob2["1750"] = 1.0
prob2["2150"] = 1.0
prob2["128x10"] = 1.0

moves = []
white = True

for idx, move in enumerate(game.mainline_moves()):
    #print(moves)
    game_state = GameState(start_fen, moves)
    #print("Game state:")
    #print(game_state.as_string())
    moves.append(move.uci())
    print("FEN: %s" % (fen))
    fen = board.fen()
    print("Player move: %s" % (move))
    l = {}
    input = game_state.as_input(b1450)
    output_1450, = b1450.evaluate(input)
    output_2150, = b2150.evaluate(input)

    p_softmax_1450 = output_1450.p_softmax(*game_state.policy_indices())
    p_moves_1450 = list(zip(game_state.moves(), p_softmax_1450))
    #p_moves_1450.sort(key = lambda tup: tup[1], reverse=True)

    p_softmax_2150 = output_2150.p_softmax(*game_state.policy_indices())
    p_moves_2150 = list(zip(game_state.moves(), p_softmax_2150))
    #p_moves_2150.sort(key = lambda tup: tup[1], reverse=True)

    print([*p_softmax_1450])
    print([*p_softmax_2150])
    plt.scatter([*p_softmax_1450], [*p_softmax_2150], c='b')
    plt.plot([0, 1], [0, 1])
    for i, m in enumerate(game_state.moves()):
        if m == move.uci():
            plt.scatter([p_softmax_1450[i]], [p_softmax_2150[i]], c='r')
    plt.show()
    '''
    l["1100"] = 0
    l["1450"] = 0
    l["1750"] = 0
    l["2150"] = 0
    l["128x10"] = 0
    l_sum = 0

    for b, name in zip([b1100, b1450, b1750, b2150, back], names):
        input = game_state.as_input(b)
        output, = b.evaluate(input)
        draw = output.d()
        win = ((1.0 - draw) + output.q()) / 2
        lose = ((1.0 - draw) - output.q()) / 2
        print("%s eval: %.0f/%.0f/%0.f" % (name, (win * 100.0), (draw * 100.0), (lose * 100.0)))
        #print("%.0f/%.0f/%0.f" % ((win * 100.0), (draw * 100.0), (lose * 100.0)))
        p_softmax = output.p_softmax(*game_state.policy_indices())
        p_moves = list(zip(game_state.moves(), p_softmax))
        p_moves.sort(key = lambda tup: tup[1], reverse=True)
        ps = [m[1]*np.log(m[1]+1e-9) for m in p_moves]
        entropy = sum(ps)
        #print([m[0] for m in p_moves])
        set = False
        for m in p_moves:
            #print(m[0])
            #print(move)
            if m[0] == move.uci():
                move_entropy = m[1]*np.log(m[1]+1e-9)
                entropy_share = move_entropy / entropy
                set = True
                l[name] = m[1]# * entropy_share
                l_sum += m[1] / 5.0
                if white:
                    prob1[name] *= l[name]
                else:
                    prob2[name] *= l[name]
        if not set:
            print("VA")
            print("%s probability of %s: %d%%" % (name, m[0], m[1]*100.0))
    '''
    board.push(move)
    white = not white

#for key in prob1.keys():
#    prob1[key] = -2 * np.log(prob1[key])
#for key in prob2.keys():
#    prob2[key] = -2 * np.log(prob2[key])
print(prob1)
print(prob2)
#print(-2*np.log(prob1))
#print(-2*np.log(prob2))
