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

    