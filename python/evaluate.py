import sys
from backends import Weights, Backend, GameState
import matplotlib.pyplot as plt
import numpy as np
import time
import random
import chess
import os

path = os.path.dirname(os.path.abspath(__file__))

#w = Weights("./384x30-t60-4300.pb.gz")
w = Weights(path + "/128x10-t60-2-5300.pb.gz")
print(Backend.available_backends())

start_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -'
b = Backend(weights=w)

v_list = []
q_list = []
reverse_q_list = []
reverse_v_list = []

top_move_p_list = []
games = 0
while games < 1:
    moves_list = []
    game_state = GameState(start_fen, moves_list)
    board = chess.Board()
    turn = 1
    move_count = 0
    while len(game_state.moves()) > 0 and move_count < 100:
        print("###############")
        fen = board.fen()
        #board.turn = not board.turn
        #reverse_fen = board.fen()
        reverse_game_state = GameState(fen, [])
        if  (reverse_game_state.as_string() == game_state.as_string()):
            print(fen)
            print(reverse_game_state.as_string())
            print(reverse_game_state.moves())
            print(game_state.as_string())
            print(game_state.moves())
        else:
            print(fen)
            print(reverse_game_state.as_string())
            print(reverse_game_state.moves())
            print(game_state.as_string())
            print(game_state.moves())
            exit()
            #exit()
        #print("#")
        #input = reverse_game_state.as_input(b)
        #output, = b.evaluate(input)
        #reverse_q_list.append(output.q() * turn * -1)
        #print(fen)
        #print(reverse_fen)
        #print("#")

        #if turn < 0 and move_count > 20 and move_count < 30:
        #reverse_v_list.append([turn * x for x in output.v()])
        #board.turn = not board.turn

        input = game_state.as_input(b)
        output, = b.evaluate(input)
        q_list.append(output.q() * turn)
        v_list.append([turn * x for x in output.v()])
        #if turn < 0 and move_count > 20 and move_count < 30:
        #reverse_v_list.append([turn * x for x in output.v()])
        p_softmax = output.p_softmax(*game_state.policy_indices())
        moves = list(zip(game_state.moves(), p_softmax))
        moves.sort(key = lambda tup: tup[1], reverse=True)
        r = random.random()
        move_p = 0
        chosen_move = None
        for move, p in moves:
            if r < p:
                moves_list.append(move)
                move_p = p
                chosen_move = move
                break
            r -= p
        #moves_list.append(moves[0][0])
        top_move_p_list.append(move_p)
        game_state = GameState(start_fen, moves_list)
        board_move = chess.Move.from_uci(chosen_move)
        board.push(board_move)
        turn = -1 * turn
        move_count += 1

    print(game_state.as_string())
    games += 1

v_list_rev = list(map(list, zip(*v_list)))
reverse_v_list_rev = list(map(list, zip(*reverse_v_list)))
#for i in range(0, len(v_list_rev)):
#    plt.plot(v_list_rev[i], 'r-')
#    plt.plot(reverse_v_list_rev[i], 'b-')
for i in range(0, 20):
    plt.plot(v_list_rev[i])
#    plt.plot(reverse_v_list_rev[i], 'rx')
plt.show()

plt.plot(q_list)
plt.show()

v_list = np.array(v_list).T
print(v_list.shape)

cov_matrix = np.cov(v_list)
values, vectors = np.linalg.eig(cov_matrix)
explained = []
for i in range(0, len(values)):
    explained.append(np.abs(values[i] / np.sum(values)))

print(explained)
#for i in range(0, 128):
#for i in range(0, 50):#
#    l = []
#    for k in range(0, len(v_list[i]) - 1):
#        l.append((v_list[i][k] + v_list[i][k+1]) / 2)

#    plt.hist(l, bins=40, range=(-1, 1))
    #plt.show()
#plt.plot(v_list[0:5])
plt.show()


exit()

inputs = []
for move in g.moves():
  g2 = GameState(start_fen, [move])
  inputs.append(g2.as_input(b))

o2 = b.evaluate(*inputs)
print(o2[0].v())
res = list(zip(g.moves(), psoftmax, [r.q() for r in o2]))


res.sort(key = lambda tup: tup[1], reverse=True)

for r in res:
  print(r[0] + ":\t%.1f" % (r[1]*100) + " \t%.1f" % (100*(-1*r[2] / 2 + 0.5)))


#  print(o.q())
#print(o.m())
#print(o.d())
#print(list(zip(g.moves(), o.p_softmax(*g.policy_indices()))))


#v = np.reshape(o.v(), (16, 8))
#print(v)
#plt.imshow(v, cmap='RdBu', vmin=-1, vmax=1)
#plt.show()
