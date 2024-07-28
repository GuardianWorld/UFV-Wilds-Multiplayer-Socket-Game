import threading

active_connections = {}
logged_users = {}
searching_for_match = {}
match_rooms = {}
stop_event = threading.Event()