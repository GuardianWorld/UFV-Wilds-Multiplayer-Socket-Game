import base64
import datetime
import os
import sqlite3
import hashlib
import json
import jwt

SECRET_KEY = "UFV_WILDS_DEV"
CARD_FOLDER = "CARDS"

# Init
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY, 
              username TEXT UNIQUE, 
              password TEXT, 
              admin INTEGER,
              matches INTEGER,
              matches_won INTEGER
              banned INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS card (
              id INTEGER PRIMARY KEY, 
              card_name TEXT, 
              card_group INTEGER, 
              forca INTEGER, 
              fofura INTEGER, 
              velocidade INTEGER, 
              tamanho TEXT, 
              idade TEXT, 
              tipo TEXT, 
              imagem TEXT, 
              last_modified TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS user_cards (
              id INTEGER PRIMARY KEY, 
              user_id INTEGER, 
              card_id INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS decks (
              id INTEGER PRIMARY KEY, 
              deck_name TEXT,
              user_id INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS deck_cards (
              id INTEGER PRIMARY KEY, 
              deck_id INTEGER, 
              card_id INTEGER)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS system_config(
                id INTEGER PRIMARY KEY, 
                key TEXT, 
                value TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS statistics(
                id INTEGER PRIMARY KEY, 
                key TEXT, 
                value INTEGER)''')
    
    # Verify if there is any ID in the statistics
    if not c.execute('''SELECT * FROM statistics''').fetchone():
        c.execute('''INSERT INTO statistics (key, value) VALUES (?, ?)''', ("users", 0))
        c.execute('''INSERT INTO statistics (key, value) VALUES (?, ?)''', ("cards", 0))
        c.execute('''INSERT INTO statistics (key, value) VALUES (?, ?)''', ("decks", 0))
        c.execute('''INSERT INTO statistics (key, value) VALUES (?, ?)''', ("matches", 0))
        c.execute('''INSERT INTO statistics (key, value) VALUES (?, ?)''', ("bans", 0))

    # Update statistics at the start
    c.execute('''UPDATE statistics SET value = (SELECT COUNT(*) FROM users) WHERE key = ?''', ("users",))
    c.execute('''UPDATE statistics SET value = (SELECT COUNT(*) FROM card) WHERE key = ?''', ("cards",))
    c.execute('''UPDATE statistics SET value = (SELECT COUNT(*) FROM decks) WHERE key = ?''', ("decks",))
    c.execute('''UPDATE statistics SET value = (SELECT COUNT(*) FROM users WHERE banned = 1) WHERE key = ?''', ("bans",))

    conn.commit()
    conn.close()

#Security Functions
def hash_password(password):
    password_bytes = password.encode('utf-8')
    sha256_hash = hashlib.sha256()
    sha256_hash.update(password_bytes)
    hashed_password = sha256_hash.hexdigest()

    return hashed_password

def validate_token(token):
    if not token:
       return None, {"status": 401, "message": "Token not found"}
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        return user_id, {"status": 200, "message": "Success"}
    except jwt.ExpiredSignatureError:
        return None, {"status": 401, "message": "Token expired", "command": "none"}
    except jwt.InvalidTokenError:
        return None, {"status": 401, "message": "Invalid token", "command": "none"}

def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=3) 
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

#DB Functions
def get_db_connection():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    return conn, c

#User Functions

def get_user_id(username):
    conn, c = get_db_connection()
    ID = c.execute('''SELECT id FROM users WHERE username = ?''', (username,)).fetchone()
    conn.close()
    return ID

def get_user(username):
    conn, c = get_db_connection()
    user = c.execute('''SELECT id, username, matches, matches_won, banned FROM users WHERE username = ?''', (username,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn, c = get_db_connection()
    user = c.execute('''SELECT * FROM users WHERE id = ?''', (user_id,)).fetchone()
    conn.close()
    return user

def is_user_banned(username):
    conn, c = get_db_connection()
    banned = c.execute('''SELECT banned FROM users WHERE username = ?''', (username,)).fetchone()
    conn.close()
    if(banned == 1):
        return True
    return False

def ban_user(username):
    try:
        conn, c = get_db_connection()
        c.execute('''UPDATE users SET banned = 1 WHERE username = ?''', (username,))
        conn.commit()
        conn.close()
        return {"status": 200, "message": "Success", "command": "ban"}
    except Exception as e:
        return {"status": 500, "message": str(e), "command": "error"}

def unban_user(username):
    try:
        conn, c = get_db_connection()
        c.execute('''UPDATE users SET banned = 0 WHERE username = ?''', (username,))
        conn.commit()
        conn.close()
        return {"status": 200, "message": "Success", "command": "unban"}
    except Exception as e:
        return {"status": 500, "message": str(e), "command": "error"}

def add_user(username, password):
    try:
        conn, c = get_db_connection()
        hashed_password = hash_password(password)
        c.execute('''INSERT INTO users (username, password, admin, matches, matches_won, banned) VALUES (?, ?, ?, ?, ?, ?)''', (username, hashed_password, 0, 0, 0, 0))
        conn.commit()
        conn.close()
        increment_statistics_users()
        return {"status": 200, "message": "Success", "command": "register"}
    except Exception as e:
        print(e)
        return {"status": 500, "message": str(e), "command": "error"}
    
def login_user(username, password):
    try:
        hashed_password = hash_password(password)

        conn, c = get_db_connection()
        user_id = c.execute('''SELECT id FROM users WHERE username = ? AND password = ?''', (username, hashed_password)).fetchone()
        
        if(is_user_banned(username)):
            return {"status": 401, "message": "User is banned", "command": "error"}
            
            
        conn.close()
        if user_id:
            token = generate_token(user_id[0])
            return {"status": 200, "message": "Success", "command": "login", "token": token}
        else:
            return {"status": 401, "message": "Invalid username or password", "command": "error"}
    except Exception as e:
        return {"status": 500, "message": str(e), "command": "error"}


# Card Functions
def add_card(card_name, card_group, forca, fofura, velocidade, tamanho, idade, tipo, imagem):
    try:
        c, conn = get_db_connection()
        last_modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        c.execute('''INSERT INTO cards (
                   card_name,
                   card_group,
                   forca,
                   fofura,
                   velocidade,
                   tamanho,
                   idade,
                   tipo,
                   imagem,
                   last_modified)''', (card_name, card_group, forca, fofura, velocidade, tamanho, idade, tipo, imagem, last_modified))

        conn.commit()
        conn.close()
        increment_statistics_cards()
        return {"status": 200, "message": "Success", "command": "none"}
    except Exception as e:
        return {"status": 500, "message": "failure to add card", "command": "none"}

def get_card_details(_data):
    try:
        data = json.loads(_data)
        user_id, status = validate_token(data.get('token'))
        if status.get('status') != 200:
            return status
        
        card_name = data.get('card_name')
        card = get_card_by_name(card_name)
        card_group = card[2]
        forca = card[3]
        fofura = card[4]
        velocidade = card[5]
        tamanho = card[6]
        idade = card[7]
        tipo = card[8]
        # For now, Placeholder
        imagem = card[9]
        last_modified = card[10]
        
        
        return {"status": 200, 
                "message": "Success", 
                "command": "get_card", 
                "card_name": card_name, 
                "card_group": card_group, 
                "forca": forca, 
                "fofura": fofura, 
                "velocidade": velocidade, 
                "tamanho": tamanho, 
                "idade": idade, 
                "tipo": tipo, 
                "imagem": imagem, 
                "last_modified": last_modified}
    except Exception as e:
        return {"status": 500, "message": "failure to get card", "command": "none"}

def get_card_by_name(name):
    return simple_command_fetchone('''SELECT * FROM card WHERE card_name = ?''', (name,))


def get_card_by_id(id): 
    return simple_command_fetchone('''SELECT * FROM card WHERE id = ?''', (id,))

def edit_card(_data):
    try:
        data = json.loads(_data)
        user_id, status = validate_token(data.get('token'))
        if status.get('status') != 200:
            return status
        conn, c = get_db_connection()

        is_admin = c.execute('''SELECT admin FROM users WHERE id = ?''', (user_id,)).fetchone()
        if is_admin != 1:
            conn.close()
            return {"status": 401, "message": "User is not an admin"}
        
        card_id = data.get('card_id')

        old_values = get_card_by_id(card_id)

        card_name = data.get('card_name')
        card_group = data.get('card_group')
        forca = data.get('forca')
        fofura = data.get('fofura')
        velocidade = data.get('velocidade')
        tamanho = data.get('tamanho')
        idade = data.get('idade')
        tipo = data.get('tipo')
        imagem = data.get('imagem')
        last_modified = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if(card_name == ""):
            card_name = old_values[1]
        if(card_group == ""):
            card_group = old_values[2]
        if(forca == ""):
            forca = old_values[3]
        if(fofura == ""):
            fofura = old_values[4]
        if(velocidade == ""):
            velocidade = old_values[5]
        if(tamanho == ""):
            tamanho = old_values[6]
        if(idade == ""):
            idade = old_values[7]
        if(tipo == ""):
            tipo = old_values[8]
        if(imagem == ""):
            image_path = old_values[9]
        else:
            image_path = save_image_to_file(imagem, card_name)

        c.execute('''UPDATE cards SET
                   card_name = ?,
                   card_group = ?,
                   forca = ?,
                   fofura = ?,
                   velocidade = ?,
                   tamanho = ?,
                   idade = ?,
                   tipo = ?,
                   imagem = ?,
                   last_modified = ?
                   WHERE id = ?''', (card_name, card_group, forca, fofura, velocidade, tamanho, idade, tipo, image_path, last_modified, card_id))

        conn.commit()
        conn.close()
        return {"status": 200, "message": "Success", "command": "none"}
    except Exception as e:
        return {"status": 500, "message": "failure to edit card", "command": "none"}

def delete_card(_data):
    try:
        data = json.loads(_data)
        user_id, status = validate_token(data.get('token'))
        if status.get('status') != 200:
            return status
        conn, c = get_db_connection()

        is_admin = c.execute('''SELECT admin FROM users WHERE id = ?''', (user_id,)).fetchone()
        if is_admin != 1:
            conn.close()
            return {"status": 401, "message": "User is not an admin"}
        
        card_id = data.get('card_id')

        c.execute('''DELETE FROM cards WHERE id = ?''', (card_id,))
        c.execute('''DELETE FROM user_cards WHERE card_id = ?''', (card_id,))
        c.execute('''DELETE FROM deck_cards WHERE card_id = ?''', (card_id,))

        conn.commit()
        conn.close()
        return {"status": 200, "message": "Success", "command": "none"}
    except Exception as e:
        return {"status": 500, "message": "failure to delete card", "command": "none"}

# Statistics Functions
def get_statistics_user():
    return simple_command_fetchone('''SELECT value FROM statistics WHERE key = ?''', ("users",))

def get_statistics_cards():
    return simple_command_fetchone('''SELECT value FROM statistics WHERE key = ?''', ("cards",))

def get_statistics_decks():
    return simple_command_fetchone('''SELECT value FROM statistics WHERE key = ?''', ("decks",))

def get_statistics_matches():
    return simple_command_fetchone('''SELECT value FROM statistics WHERE key = ?''', ("matches",))

def get_statistics_banned():
    return simple_command_fetchone('''SELECT value FROM statistics WHERE key = ?''', ("bans",))

def increment_statistics_users():
    execute_simple_command('''UPDATE statistics SET value = value + 1 WHERE key = ?''', ("users",))

def increment_statistics_cards():
    execute_simple_command('''UPDATE statistics SET value = value + 1 WHERE key = ?''', ("cards",))
    
def increment_statistics_decks():
    execute_simple_command('''UPDATE statistics SET value = value + 1 WHERE key = ?''', ("decks",))
    
def increment_statistics_matches():
    execute_simple_command('''UPDATE statistics SET value = value + 1 WHERE key = ?''', ("matches",))
    
def increment_statistics_bans():
    execute_simple_command('''UPDATE statistics SET value = value + 1 WHERE key = ?''', ("bans",))
    
def decrement_statistics_users():
    execute_simple_command('''UPDATE statistics SET value = value - 1 WHERE key = ?''', ("users",))

def decrement_statistics_cards():
    execute_simple_command('''UPDATE statistics SET value = value - 1 WHERE key = ?''', ("cards",))

def decrement_statistics_decks():
    execute_simple_command('''UPDATE statistics SET value = value - 1 WHERE key = ?''', ("decks",))



# Auxiliary Functions
def execute_simple_command(command, params):
    conn, c = get_db_connection()
    c.execute(command, params)
    conn.commit()
    conn.close()

def simple_command_fetchone(command, params):
    conn, c = get_db_connection()
    result = c.execute(command, params).fetchone()
    conn.close()
    return result

def get_9_random_cards():
    conn, c = get_db_connection()
    cards = c.execute('''SELECT * FROM cards ORDER BY RANDOM() LIMIT 9''').fetchall()
    conn.close()
    return cards

def get_user_cards(user_id):
    conn, c = get_db_connection()
    cards = c.execute('''SELECT * FROM user_cards WHERE user_id = ?''', (user_id,)).fetchall()
    conn.close()
    return cards

def get_deck_cards(deck_id):
    conn, c = get_db_connection()
    cards = c.execute('''SELECT * FROM deck_cards WHERE deck_id = ?''', (deck_id,)).fetchall()
    conn.close()
    return cards

def get_user_decks(user_id):
    conn, c = get_db_connection()
    decks = c.execute('''SELECT * FROM decks WHERE user_id = ?''', (user_id,)).fetchall()
    conn.close()
    return decks

def get_deck_by_id(deck_id):
    conn, c = get_db_connection()
    deck = c.execute('''SELECT * FROM decks WHERE id = ?''', (deck_id,)).fetchone()
    conn.close()
    return deck

def get_all_usernames():
    conn, c = get_db_connection()
    usernames = c.execute('''SELECT username FROM users''').fetchall()
    conn.close()
    return usernames

# Card File Functions
def save_image_to_file(image_base64, card_name):
    image_data = base64.b64decode(image_base64)
    file_path = os.path.join(CARD_FOLDER, f"{card_name}.png")
    with open(file_path, 'wb') as image_file:
        image_file.write(image_data)
    return file_path