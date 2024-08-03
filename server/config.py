import threading

active_connections = {}
logged_users = {}
searching_for_match = {}
match_rooms = []
stop_event = threading.Event()
log_event_level = 5
delay_for_lag = 0.1