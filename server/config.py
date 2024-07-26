import threading

active_connections = {}
logged_users = {}
stop_event = threading.Event()