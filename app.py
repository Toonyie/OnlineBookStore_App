# app.py
from flask import Flask, jsonify, request, session
import sqlite3
from pathlib import Path
import bcrypt
import secrets
app = Flask(__name__)
SESSIONS = {}  
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bookstore.db"

#This functions gets the session token (if any) to validate authorization
def get_token_user():
    "Return the user dict for the token in the Authorization header, or None."
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split()
    print(parts)
    # Expect: "Bearer <token>"
    if len(parts) == 2 and parts[0].lower() == "bearer":
        token = parts[1]
        return SESSIONS.get(token)
    return None

def is_authenticated():
    return get_token_user() is not None

def current_user_is_manager():
    user = get_token_user()
    return user is not None and user.get("role") == "manager"

#Create a user account
def create_account(username, password, email, is_customer):
    conn = sqlite3.connect(DB_PATH)
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) #Encode the password string into btyes
    print(hashed_pw)
    print(hashed_pw.decode('utf-8'))
    try:
        cur = conn.cursor()
        #Here we will store the encrypted password by decoding it which returns a string
        cur.execute("INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)", (username, hashed_pw.decode('utf-8'), email, "customer" if is_customer else "manager")) 
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
        cur.execute("SELECT user_id, username, password_hash, role FROM users WHERE username = ?", (username,))
        row = cur.fetchone()

        #If a username exists in the database
        if not row:
            print("Username not found.")
            return None
        user_id, db_username, stored_hash, role = row

        # Compare entered password with stored hash by encoding both into bytes
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            print("Login successful for:", username)
            cur.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            return{
                    "id": user_id,
                    "username": db_username,
                    "role": role
                    }
        else:
            print("Password failed. Try Again...")
            return None
        
    except sqlite3.Error as e:
        print("Database error")
        return None
    finally:
        conn.close()

#Logging out by clearing the Sessions token
def logout():
    SESSIONS.clear()
    print("Logged out.")
    return True

#Searching for books based on title and author
def booksearch(title = None, author = None):
    conn = sqlite3.connect(DB_PATH)
    cols = "book_id, title, author, price_buy, price_rent, active"
    try: #Depending on the request, we get all the books and append them to a results list
        curr = conn.cursor()
        if title and not author:
            curr.execute(f"SELECT {cols} FROM books WHERE title = ?", (title,))
        elif author and not title:
            curr.execute(f"SELECT {cols} FROM books WHERE author = ?", (author,))
        elif author and title:
            curr.execute(f"SELECT {cols} FROM books WHERE title = ? AND author = ?", (title, author,))    
        rows = curr.fetchall()
        results = []
        for row in rows:
            results.append({
                "book_id": row[0],
                "title": row[1],
                "author": row[2],
                "price_buy": row[3],
                "price_rent": row[4],
                "active": row[5]
            })
        return results
    
    except sqlite3.Error as e:
        print("Database error:", e)
        return []
    
    finally:
        conn.close()
    

#------------------------Manager Functions --------------
#Manager views all orders
def view_orders():
    if not is_authenticated() or not current_user_is_manager():
        return jsonify(ok=False, message="Forbidden: manager only"), 403
    try:
        conn = sqlite3.connect(DB_PATH)
        curr = conn.cursor()
        cols = "user_id, status, payed, created_at"
        curr.execute(f"SELECT {cols} FROM orders")
        rows = curr.fetchall()
        results = []
        for row in rows:
            results.append({
                "user_id": row[0],
                "status": row[1],
                "payed": row[2],
                "created_at": row[3],
                })
        return results
    
    except sqlite3.Error as e:
        print("Database error:", e)
        return []
    finally:
        conn.close()

#Manager updates order statuses
def update_status(orderid, status):
    try:
        conn = sqlite3.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(f"UPDATE orders SET status = ? WHERE order_id = ?", (status, orderid,))
        conn.commit()
        print(f"Order {orderid} updated to status '{status}'.")
        return True
    except sqlite3.Error as e:
        print("Database error:", e)
        return False
    finally:
        conn.close()

#Add book to book list
def add_book(title, author, price_buy, price_rent):
    try:
        conn = sqlite3.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(f"INSERT INTO books (title, author, price_buy, price_rent) VALUES (?, ?, ?, ?)", (title, author, float(price_buy), float(price_rent)))
        conn.commit()
        print(f"Added {title} from {author} with price {price_buy} for buying and price {price_rent} for rent")
        return True
    except sqlite3.Error as e:
        print("Database error:", e)
        return False
    finally:
        conn.close()

#Change book status
def change_book_status(book_id, status):
    try:
        conn = sqlite3.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(f"UPDATE books SET active = ? WHERE book_id = ?", (status, book_id,))
        conn.commit()
        print(f"Changed {book_id} status to {status}")
        return True
    except sqlite3.Error as e:
        print("Database error:", e)
        return False
    finally:
        conn.close()
    
@app.route("/", methods=["GET"])
def root():
    return jsonify(ok=True, message="API running")

@app.route("/createaccount", methods=["POST"])
def route_create_account():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    email    = data.get("email")
    is_customer = data.get("is_customer", True)
    if not username or not password or not email:
        return jsonify(ok=False, message="Missing username/password/email"), 400

    ok = create_account(username, password, email, is_customer)
    if ok:
        return jsonify(ok=True, message="Account created"), 201
    else:
        # if your create_account prints specific errors, you could surface them here
        return jsonify(ok=False, message="DB error (possibly duplicate username/email)"), 409

@app.route("/loginaccount")
def route_to_login():

    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify(ok=False, message="Missing username/password"), 400

    user = login(username, password)
    if not user:
        return jsonify(ok=False, message="Invalid credentials"), 401

    # check if this specific user already logged in
    for token, sess_user in SESSIONS.items():
        if sess_user["id"] == user["id"]:
            return jsonify(
                ok=False,
                message="This user is already logged in."
            ), 400
        
    #Otherwise create a session token using the secrets library and store it in memory
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = user
    print(SESSIONS)
    return jsonify(
        ok=True,
        message="Login successful",
        role=user["role"],
        token=token
    ), 200

@app.route("/logout")
def route_to_logout():
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split()
    #Splits the header into two parts. [Authorization, token]
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return jsonify(ok=False, message="Missing or invalid Authorization header"), 401
    token = parts[1]
    if token in SESSIONS:
        del SESSIONS[token]
        print("Logged out token:", token)
        return jsonify(ok=True, message="Logged out successfully."), 200
    else:
        return jsonify(ok=False, message="Invalid token"), 401

@app.route("/addbook", methods = ["POST"])
def addbook():
    user = get_token_user() #Confirm Authentication
    if not user:
        return jsonify(ok=False, message="Auth required"), 401
    if not current_user_is_manager():
        return jsonify(ok=False, message="Forbidden: manager only"), 403
    
    data = request.get_json(silent=True) or {} #Get the data from the json from client then input it into the addbook function
    title = data.get("title")
    author = data.get("author")
    price_buy = data.get("price_buy")
    price_rent = data.get("price_rent")
    ok = add_book(title, author, price_buy, price_rent)
    if ok:
        return jsonify(ok=True, message="Book Added!"), 201
    else:
        return jsonify(ok=False, message="Failed to add book"), 409

@app.get("/books")
def route_booksearch():
    user = get_token_user()
    if not user:
        return jsonify(ok=False, message="Auth required"), 401
    if user["role"] == "manager":
        return jsonify(ok=False, message="Forbidden: customer only"), 403
    data = request.get_json(silent = True) or {}   
    title_input = data.get("title")
    author_input = data.get("author")
    books = booksearch(title=title_input, author=author_input)
    return jsonify(ok=True, count=len(books), books=books), 200

if __name__ == "__main__":
    app.run(debug=True)
    