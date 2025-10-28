# app.py
from flask import Flask, jsonify
import sqlite3
from pathlib import Path
import bcrypt

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bookstore.db"
CURRENT_USER = None #Just what we will use to authenticate the user

def is_authenticated():
    return CURRENT_USER is not None

#Create a user account
def create_account(username, password, email, is_customer):
    conn = sqlite3.connect(DB_PATH)
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) #Encode the password string into bits

    try:
        cur = conn.cursor()
        #Here we will store the encrypted password by decoding it which returns a string
        cur.execute("INSERT INTO users (username, password, email, role) VALUES (?, ?, ?, ?)", (username, hashed_pw.decode('utf-8'), email, "customer" if is_customer else "manager")) 
        conn.commit()
        print("Account created!")
        return True 
    except sqlite3.Error as e:
        print("Database error:", e)
        return False
    finally:
        conn.close()

#Logging in
def login(username, password):
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cur.fetchone()

        #If a username exists in the database
        if not row:
            print("Username not found.")
            return False
        
        stored_hash = row[0]  # get the hash string from the DB
        # Compare entered password with stored hash by encoding both into bytes
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            print("Login successful for:", username)
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            global CURRENT_USER
            CURRENT_USER = [row[0], row[1],row[3]]
            return True
        else:
            print("Password failed. Try Again...")
            return False
        
    except sqlite3.Error as e:
        print("Database error")
        return False
    finally:
        conn.close()

#Logging out
def logout():
    global CURRENT_USER
    CURRENT_USER = None
    print("Logged out.")
    return True

if __name__ == "__main__":
    app.run(debug=True)