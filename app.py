# app.py
from dotenv import load_dotenv
load_dotenv('database.env')
from flask import Flask, jsonify, request, session
import bcrypt
import secrets
import os, smtplib
from email.message import EmailMessage
import mysql.connector
from mysql.connector import pooling

app = Flask(__name__)
SESSIONS = {}  

#Create a connection pool to ensure an adequete response time
dbconfig = {
    "host": os.environ.get("DB_HOST", "localhost"),
    "user": os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASS"),
    "database": os.environ.get("DB_NAME", "bookstore_db"),
    "port": os.environ.get("DB_PORT", 3306)
}

try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name="bookstore_pool",
        pool_size=5,
        pool_reset_session=True,
        **dbconfig
    )
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")
    exit(1)
    
#Connect to MySQL database
def get_db_connection():
    try:
        # Get a connection from the pool instead of making a new one
        connection = connection_pool.get_connection()

        # Ensure the connection is actually alive
        if not connection.is_connected():
            connection.reconnect(attempts=3, delay=0)

        return connection
    except mysql.connector.Error as err:
        print(f"Error getting connection from pool: {err}")
        raise


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
    conn = get_db_connection()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) #Encode the password string into btyes
    print(hashed_pw)
    print(hashed_pw.decode('utf-8'))
    try:
        cur = conn.cursor(buffered=True)
        #Here we will store the encrypted password by decoding it which returns a string
        cur.execute("INSERT INTO users (username, password_hash, email, role) VALUES (%s, %s, %s, %s)", (username, hashed_pw.decode('utf-8'), email, "customer" if is_customer else "manager")) 
        conn.commit()
        print("Account created!")
        return True 
    except mysql.connector.Error as e:
        print("Database error:", e)
        return False
    finally:
        conn.close()

#Logging in
def login(username, password):
    conn = get_db_connection()
    try:
        cur = conn.cursor(buffered=True)
        cur.execute("SELECT user_id, username, password_hash, role FROM users WHERE username = %s", (username,))
        row = cur.fetchone()

        #If a username exists in the database
        if not row:
            print("Username not found.")
            return None
        user_id, db_username, stored_hash, role = row

        # Compare entered password with stored hash by encoding both into bytes
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            print("Login successful for:", username)
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            row = cur.fetchone()
            return{
                    "id": user_id,
                    "username": db_username,
                    "role": role
                    }
        else:
            print("Password failed. Try Again...")
            return None
        
    except mysql.connector.Error as e:
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
    conn = get_db_connection()
    cols = "book_id, title, author, price_buy, price_rent, quantity"
    try: #Depending on the request, we get all the books and append them to a results list
        curr = conn.cursor(buffered=True)
        if title and not author:
            curr.execute(f"SELECT {cols} FROM books WHERE title = %s", (title,))
        elif author and not title:
            curr.execute(f"SELECT {cols} FROM books WHERE author = %s", (author,))
        elif author and title:
            curr.execute(f"SELECT {cols} FROM books WHERE title = %s AND author = %s", (title, author,))    
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
    
    except mysql.connector.Error as e:
        print("Database error:", e)
        return []
    
    finally:
        conn.close()
        
def get_user_email(user_id):
    conn = get_db_connection()
    try:
        cur = conn.cursor(buffered=True)
        cur.execute("SELECT email FROM users WHERE user_id = %s", (user_id,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()

#Helper function for checkout
def checkout(user, cart):
    conn = get_db_connection()
    counts = {}

    try:
        curr = conn.cursor(buffered=True)

        # 1) Count how many of each book_id are being ordered
        for item in cart:
            book_id = item.get("book_id")
            otype   = item.get("type")
            if book_id is None or otype not in ("buy", "rent"):
                return jsonify(ok=False, message="Invalid cart item"), 400
            counts[book_id] = counts.get(book_id, 0) + 1

        # 2) Check stock for all books
        for book_id, qty_needed in counts.items():
            curr.execute("SELECT quantity FROM books WHERE book_id = %s", (book_id,))
            row = curr.fetchone()
            if not row:
                return jsonify(ok=False, message=f"Book {book_id} not found"), 404
            if row[0] < qty_needed:
                return jsonify(ok=False, message=f"Not enough stock for book {book_id}"), 409
            
        has_rent = any(item["type"] == "rent" for item in cart)

        # 3) Create order 
        curr.execute(
            "INSERT INTO orders (user_id, status, payed, created_at) "
            "VALUES (%s, %s, %s, NOW())",
            (user["id"], "Pending", 0)
        )
        order_id = curr.lastrowid
        total = 0.0

        items_for_email = []  

        # 4) Insert order items + decrement quantity
        for item in cart:
            b_id  = item["book_id"]
            otype = item["type"]

            # pull full book info for email + pricing
            curr.execute(
                "SELECT title, author, price_buy, price_rent FROM books WHERE book_id = %s",
                (b_id,)
            )
            row = curr.fetchone()
            if not row:
                return jsonify(ok=False, message=f"Book {b_id} not found"), 404

            title, author, price_buy, price_rent = row
            unit_price = price_buy if otype == "buy" else price_rent
            subtotal = unit_price  # qty=1 per cart entry
            total += subtotal

            # insert line item
            curr.execute(
                "INSERT INTO order_items (order_id, book_id, item_type, unit_price, quantity) "
                "VALUES(%s, %s, %s, %s, %s)",
                (order_id, b_id, otype, unit_price, 1)
            )

            # decrement stock
            curr.execute(
                "UPDATE books SET quantity = quantity - 1 WHERE book_id = %s",
                (b_id,)
            )

            #store email line item
            items_for_email.append({
                "title": title,
                "author": author,
                "type": otype,
                "qty": 1,
                "unit_price": float(unit_price),
                "subtotal": float(subtotal)
            })

        # 5) Set order status based on cart contents
        if has_rent:
            new_status = "Pending Rental Payment"
            payed_val = 0
        else:
            new_status = "Paid"
            payed_val = 1

        curr.execute(
            "UPDATE orders SET status = %s, payed = %s WHERE order_id = %s",
            (new_status, payed_val, order_id)
        )

        conn.commit()

        # send email AFTER commit
        email_addr = get_user_email(user["id"])
        if email_addr:
            send_bill_email(email_addr, items_for_email, total)  

        return jsonify(ok=True, message="Order placed!", order_id=order_id), 201

    except mysql.connector.Error as e:
        conn.rollback()
        print("Database error:", e)
        return jsonify(ok=False, message=str(e)), 500

    finally:
        conn.close()



#send billing email
def send_bill_email(to_email, items, grand_total):
    #To send an email the os env email and password has to be set before app.py to run if you want to send emails
    sender = os.getenv("BOOKSTORE_EMAIL")
    password = os.getenv("BOOKSTORE_EMAIL_PASS")

    if not sender or not password:
        print("Email not configured; skipping send.")
        return False
    #Receipt text
    lines = []
    lines.append(f"Thanks for your order! 🎉")

    for it in items:
        lines.append(f'{it["title"]} — {it["author"]}')
        lines.append(
            f'  Type: {it["type"].upper()}  |  Qty: {it["qty"]}  '
            f'|  Unit: ${it["unit_price"]:.2f}  |  Subtotal: ${it["subtotal"]:.2f}'
        )
        lines.append("")  # blank line between items

    lines.append("-" * 45)
    lines.append(f"Grand Total: ${grand_total:.2f}")
    lines.append("")
    lines.append("If you rented books, please return by the due date.")
    lines.append("Thank you for shopping with us!")

    body = "\n".join(lines)


    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = "Your Bookstore Receipt"
    msg.set_content(body)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender, password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Email send failed:", e)
        return False
        
#------------------------Manager Functions --------------
#Manager views all orders (Simple Fetch response)
def view_orders():
    try:
        conn = get_db_connection()
        curr = conn.cursor(buffered=True)
        cols = "order_id,user_id, status, payed, created_at"
        curr.execute(f"SELECT {cols} FROM orders")
        rows = curr.fetchall()
        results = []
        for row in rows:
            results.append({
                "order_id": row[0],
                "user_id": row[1],
                "status": row[2],
                "payed": row[3],
                "created_at": row[4],
                })
        return results
    
    except mysql.connector.Error as e:
        print("Database error:", e)
        return []
    finally:
        conn.close()


#Manager updates order statuses (Rent goes from Pending to Retuned for example)
def update_status(orderid, status, paid=None):
    if not status:
        return False

    # Decide what payed should be
    paid_value = 1 if (status.lower() == "paid" or status.lower() == "returned") else 0
    
    conn = get_db_connection()
    try:
        curr = conn.cursor(buffered=True)
        curr.execute(
            "UPDATE orders SET status = %s, payed = %s WHERE order_id = %s",
            (status, paid_value, orderid)
        )
        conn.commit()
        return curr.rowcount > 0  # True if something updated
    except mysql.connector.Error as e:
        print("Database error:", e)
        return False
    finally:
        conn.close()

#Add book to book ()
def add_book(title, author, price_buy, price_rent, quantity = 1):
    conn = get_db_connection()
    try:
        curr = conn.cursor(buffered=True)
        #Check if we are adding a duplicate book
        curr.execute(
            "SELECT book_id FROM books WHERE title = %s AND author = %s",
            (title, author)
        )
        existing = curr.fetchone()
        if existing:
            #If we have a duplicate, update the quantity
            curr.execute(
                "UPDATE books SET quantity = quantity + %s WHERE book_id = %s",
                (int(quantity), existing[0])
            )
        else:
            #Otherwise insert a new book
            curr.execute(
                "INSERT INTO books (title, author, price_buy, price_rent, quantity) "
                "VALUES (%s, %s, %s, %s, %s)",
                (title, author, float(price_buy), float(price_rent), int(quantity))
            )
        conn.commit()
        return True
    except mysql.connector.Error as e:
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
    want_manager = data.get("want_manager",False)
    
    if not username or not password:
        return jsonify(ok=False, message="Missing username/password"), 400

    user = login(username, password)
    if not user:
        return jsonify(ok=False, message="Invalid credentials"), 401
    
    #Check if the user is trying to log in as a manager but isn't a manager
    if want_manager and user["role"] != "manager":
        return jsonify(ok=False, message="This account is not a manager."), 403

    if not want_manager and user["role"] == "manager":
        return jsonify(ok=False, message="This account is not a customer."), 403
    
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
    quantity = data.get("quantity",1)
    
    if not title or not author or price_buy is None or price_rent is None:
        return jsonify(ok=False, message="Missing book fields"), 400
    
    ok = add_book(title, author, price_buy, price_rent, quantity)
    if ok:
        return jsonify(ok=True, message="Book Added!"), 201
    else:
        return jsonify(ok=False, message="Failed to add book"), 409

@app.route("/orders")
def route_view_orders():
    user = get_token_user() #Confirm Authentication
    if not user:
        return jsonify(ok=False, message="Auth required"), 401
    if not current_user_is_manager():
        return jsonify(ok=False, message="Forbidden: manager only"), 403
    
    orders = view_orders() #Run view orders function
    return jsonify(ok = True, count=len(orders), orders=orders), 200 #Return all information of orders from database

@app.post("/orders/<int:orderid>/status")
def route_update_status(orderid):
    user = get_token_user()
    if not user:
        return jsonify(ok=False, message="Auth required"), 401
    if not current_user_is_manager():
        return jsonify(ok=False, message="Forbidden: manager only"), 403

    data = request.get_json(silent=True) or {}
    status = data.get("status")
    if not status:
        return jsonify(ok=False, message="Missing status"), 400

    ok = update_status(orderid, status)
    if ok:
        return jsonify(ok=True, message="Order updated"), 200
    else:
        return jsonify(ok=False, message="Order not found"), 404
    
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
        return jsonify(ok=False, message="Forbidden: customer only"), 403
    
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
    