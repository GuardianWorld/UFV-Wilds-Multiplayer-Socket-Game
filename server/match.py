import random
import sys
import socket
import json
import threading
import time
import signal
import database

from config import active_connections, logged_users, stop_event, searching_for_match, match_rooms, log_event_level

def search_match():
    matched_players = []
    while not stop_event.is_set():
        if(len(searching_for_match) >= 3):
            matched_players = random.sample(list(searching_for_match.items()), 3)
            for player in matched_players:
                del searching_for_match[player[0]]
            match_rooms.append(matched_players)
            # make a new thread for the match
            match_thread = threading.Thread(target=play_field, args=(matched_players,))
            match_thread.start()
            matched_players.clear()
            time.sleep(0.2)
        else:
            time.sleep(3)

def waiting_for_match(player_name, player_socket):
    searching_for_match[player_name] = player_socket
    return {"status": 200, "message": "Searching for match...", "command": "match_wait"}

def player_searching(player_name):
    if player_name in searching_for_match:
        return True
    return False

def player_in_match(player_name):
    for match in match_rooms:
        if player_name in match:
            return True
    return False

def play_field(matched_players):
    player1_name = matched_players[0][0]
    player1_socket = matched_players[0][1]
    player2_name = matched_players[1][0]
    player2_socket = matched_players[1][1]
    player3_name = matched_players[2][0]
    player3_socket = matched_players[2][1]
    
    if(log_event_level >= 5):
        print(f"[*] Match started between {player1_name}, {player2_name} and {player3_name}")
    
    player1_socket.send(json.dumps({"status": 200, "message": "match", "command": "match_start", "player_1": player1_name, "player_2": player2_name, "player_3": player3_name}).encode())
    player2_socket.send(json.dumps({"status": 200, "message": "match", "command": "match_start", "player_1": player1_name, "player_2": player2_name, "player_3": player3_name}).encode())
    player3_socket.send(json.dumps({"status": 200, "message": "match", "command": "match_start", "player_1": player1_name, "player_2": player2_name, "player_3": player3_name}).encode())
    time.sleep(0.2)
    
    player_round = random.choice([player1_name, player2_name, player3_name])
    
    
    while not stop_event.is_set():
        player1_socket.send(json.dumps({"status": 200, "message": "play_field WIP!", "command": "match_end"}).encode())
        player2_socket.send(json.dumps({"status": 200, "message": "play_field WIP!", "command": "match_end"}).encode())
        player3_socket.send(json.dumps({"status": 200, "message": "play_field WIP!", "command": "match_end"}).encode())
        break
        try:
            player1_socket.send(json.dumps({"status": 200, "message": "Your turn!", "command": "your_turn"}).encode())
            player2_socket.send(json.dumps({"status": 200, "message": "Opponent's turn!", "command": "opponent_turn"}).encode())
            player3_socket.send(json.dumps({"status": 200, "message": "Opponent's turn!", "command": "opponent_turn"}).encode())
            
            player1_move = player1_socket.recv(2048).decode()
            
            
            player2_move = player2_socket.recv(2048).decode()
            
            player1_socket.send(json.dumps({"status": 200, "message": "Opponent's move: " + player2_move, "command": "move"}).encode())
            player2_socket.send(json.dumps({"status": 200, "message": "Opponent's move: " + player1_move, "command": "move"}).encode())
        except:
            break
    print("[*] Match ended.")
    match_rooms.remove(matched_players)
    #find on match_rooms
    return