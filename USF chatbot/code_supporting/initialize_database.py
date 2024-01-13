#!/bin/python
# You need to run this to initialize the database before running the chatbot
 
import sqlite3
import os
path = os.path.dirname(os.path.abspath(__file__))
print(path)

# create a user table that contains email, name, and conversation
def create_user_table():
    try:
        conn = sqlite3.connect(f'{path}\\chat_history.db')
        print("Opened database successfully!")
    except:
        print("Failed to open database!")
        exit(0)
    c = conn.cursor()
    c.execute("""DROP TABLE IF EXISTS users;""")
    c.execute("""CREATE TABLE IF NOT EXISTS users 
              (
                email TEXT CONSTRAINT users_pk PRIMARY KEY,
                u_number TEXT,
                name TEXT, 
                conversation TEXT
              );
              
              """)
    conn.commit()
    conn.close()
    
def populate_user_table(csv_file_name):
    import csv
    # this function will open the given csv file and populate the user table
    # with the data in the csv file
    try:
        conn = sqlite3.connect('chat_history.db')
        print("Opened database successfully")
    except:
        print("Failed to open database")
        exit(0)
    c = conn.cursor()
    with open(csv_file_name, 'r') as fin:
        dr = csv.DictReader(fin)
        to_db = [(i['email'],i['u_number'], i['name'], i['conversation']) for i in dr]
    c.executemany("INSERT INTO users (email,u_number, name, conversation) VALUES (?, ?, ?, ?);", to_db)
    conn.commit()
    conn.close()
    
if __name__ == '__main__':
    create_user_table()
    populate_user_table('users_deatils.csv')