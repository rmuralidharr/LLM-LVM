import sqlite3

# open database connection and list all users

def list_users():
    try:
        conn = sqlite3.connect('chat_history.db')
        print("Opened database successfully")
    except:
        print("Failed to open database")
        exit(0)
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()

if __name__ == '__main__':
    list_users()