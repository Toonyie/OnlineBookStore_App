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
    cols = "book_id, title, author, price_buy, price_rent, quantity"
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
                "quantity": row[5]
            })
        return results
    
    except sqlite3.Error as e:
        print("Database error:", e)
        return []
    
    finally:
        conn.close()
    
#Helper function for checkout
def checkout(user, cart):
    conn = sqlite3.connect(DB_PATH)
    counts = {}

    try:
        curr = conn.cursor()

        # 1) Count how many of each book_id are being ordered
        for item in cart:
            book_id = item.get("book_id")
            otype   = item.get("type")
            if book_id is None or otype not in ("buy", "rent"):
                return jsonify(ok=False, message="Invalid cart item"), 400
            counts[book_id] = counts.get(book_id, 0) + 1

        # 2) Check stock for all books
        for book_id, qty_needed in counts.items():
            curr.execute("SELECT quantity FROM books WHERE book_id = ?", (book_id,))
            row = curr.fetchone()
            if not row:
                return jsonify(ok=False, message=f"Book {book_id} not found"), 404
            if row[0] < qty_needed:
                return jsonify(ok=False, message=f"Not enough stock for book {book_id}"), 409

        # 3) Create order
        curr.execute(
            "INSERT INTO orders (user_id, status, payed, created_at) "
            "VALUES (?, ?, ?, datetime('now'))",
            (user["id"], "Pending", 0)
        )
        order_id = curr.lastrowid

        # 4) Insert order items + decrement quantity
        for item in cart:
            b_id  = item["book_id"]
            otype = item["type"]

            # get correct price for this item
            curr.execute("SELECT price_buy, price_rent FROM books WHERE book_id = ?", (b_id,))
            row = curr.fetchone()
            if not row:
                return jsonify(ok=False, message=f"Book {b_id} not found"), 404

            price_buy, price_rent = row
            unit_price = price_buy if otype == "buy" else price_rent

            # insert line item
            curr.execute(
                "INSERT INTO order_items (order_id, book_id, item_type, unit_price, quantity) "
                "VALUES (?, ?, ?, ?, ?)",
                (order_id, b_id, otype, unit_price, 1)
            )

            # decrement stock
            curr.execute(
                "UPDATE books SET quantity = quantity - 1 WHERE book_id = ?",
                (b_id,)
            )

        # 5) Set order status based on cart contents
        has_rent = any(item["type"] == "rent" for item in cart)
        new_status = "Pending Rental Payment" if has_rent else "Pending Purchase Payment"

        curr.execute(
            "UPDATE orders SET status = ? WHERE order_id = ?",
            (new_status, order_id)
        )

        conn.commit()
        return jsonify(ok=True, message="Order placed!", order_id=order_id), 201

    except sqlite3.Error as e:
        conn.rollback()
        print("Database error:", e)
        return jsonify(ok=False, message=str(e)), 500

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
def add_book(title, author, price_buy, price_rent, quantity = 1):
    try:
        conn = sqlite3.connect(DB_PATH)
        curr = conn.cursor()
        curr.execute(f"INSERT INTO books (title, author, price_buy, price_rent) VALUES (?, ?, ?, ?)", (title, author, float(price_buy), float(price_rent), int(quantity)))
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
        curr.execute(f"UPDATE books SET quantity = ? WHERE book_id = ?", (status, book_id,))
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


@app.route("/checkout", methods=["POST"])
def route_checkout():
    user = get_token_user()
    #Check authentication
    if not user:
        return jsonify(ok=False, message="Auth required"), 401
    if user["role"] != "customer" :
        return jsonify(ok=False, message="Forbidden: customer only"), 40
    
    data = request.get_json(silent = True) or {}   
    cart = data.get("cart", [])
    
    if not cart:
            return jsonify(ok=False, message="Cart is empty"), 400
    try:
        return checkout(user, cart)
    except Exception as e:
        print("Checkout crash:", e)
        return jsonify(ok=False, message=str(e)), 500
if __name__ == "__main__":
    app.run(debug=True)
    