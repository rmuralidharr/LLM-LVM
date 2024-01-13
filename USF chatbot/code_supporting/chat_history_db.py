def is_email_in_database(email):
    import sqlite3
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    rows = c.fetchall()
    return len(rows) > 0 # will be true if the user is in the database
    
def fetch_u_number_from_database(email):
    import sqlite3
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    rows = c.fetchall()
    return rows[0][1] # will be true if the user is in the database

def fetch_name_from_database(email):
    import sqlite3
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    rows = c.fetchall()
    return rows[0][2] # will contain the name field

def insert_new_user_into_database(u_number,email, name, conversation):
    import sqlite3
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)", (email,u_number, name, ""))
    conn.commit()
    conn.close()

def fetch_user_from_database(email):
    import sqlite3
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    rows = c.fetchall()
    return (rows[0][0], rows[0][1], rows[0][2], rows[0][3]) # will contain the fields u_number,email,  name, status, comversation

def insert_conversation(email, conversation):
    import sqlite3
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("UPDATE users SET conversation=? WHERE email=?", (conversation, email))
    conn.commit()
    conn.close()

def fetch_conersations_from_database(email):
    import sqlite3
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    rows = c.fetchall()
    return rows[0][4]