import random
import sys
import socket
import json
import threading
import time
import signal
import database

from config import active_connections, logged_users, stop_event, searching_for_match, match_rooms

def search_match(player_socket, player_name):
    searching_for_match[player_name] = player_socket
    player_socket.send(json.dumps({"status": 200, "message": "Searching for match...", "command": "searching"}).encode())
    while not stop_event.is_set():
        for second_player in searching_for_match:
            if second_player != player_name:
                match_rooms[len(match_rooms)] = {(player_name, player_socket), (second_player, searching_for_match[second_player])}
                player_socket.send(json.dumps({"status": 200, "message": "Match found!", "command": "match"}).encode())
                searching_for_match[second_player].send(json.dumps({"status": 200, "message": "Match found!", "command": "match"}).encode())
                
                del searching_for_match[player_name]
                del searching_for_match[second_player]
        if player_name in match_rooms:
            player_socket.send(json.dumps({"status": 200, "message": "Match found!", "command": "match"}).encode())
            break
        time.sleep(1)


def play_field(player1, player2):
    player1_name = player1[0]
    player1_socket = player1[1]
    player2_name = player2[0]
    player2_socket = player2[1]
    
    player1_socket.send(json.dumps({"status": 200, "message": "Game started!", "command": "match start"}).encode())
    player2_socket.send(json.dumps({"status": 200, "message": "Game started!", "command": "match start"}).encode())
    
    player_round = random.choice([player1_name, player2_name])
    
    
    while not stop_event.is_set():
        try:
            player1_socket.send(json.dumps({"status": 200, "message": "Your turn!", "command": "your_turn"}).encode())
            player2_socket.send(json.dumps({"status": 200, "message": "Opponent's turn!", "command": "opponent_turn"}).encode())
            
            player1_move = player1_socket.recv(1024).decode()
            player2_move = player2_socket.recv(1024).decode()
            
            player1_socket.send(json.dumps({"status": 200, "message": "Opponent's move: " + player2_move, "command": "move"}).encode())
            player2_socket.send(json.dumps({"status": 200, "message": "Opponent's move: " + player1_move, "command": "move"}).encode())
        except:
            break