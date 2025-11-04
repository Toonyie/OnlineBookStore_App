#Client Functions that the client_test.py and tinkter.py will use
import requests
BASE_URL = "http://127.0.0.1:5000"

def create_account(username, email, password, is_customer=True):
    data = {
        "username": username,
        "email": email,
        "password": password,
        "is_customer": is_customer
    }
    #Send a request to createaccount route and with the jsonified data. Afterwards it gets the json return file + the status code
    response = requests.post(f"{BASE_URL}/createaccount", json=data)
    return response.status_code, response.json()

def login_account(username, password):
    data = {
        "username": username,
        "password": password
    }
    response = requests.get(f"{BASE_URL}/loginaccount", json=data)
    return response.status_code, response.json()

def logout():
    response = requests.get(f"{BASE_URL}/logout")
    return response.status_code, response.json()

def addbook(title, author, price_buy, price_rent):
    data = {
        "title": title,
        "author": author,
        "price_buy": price_buy,
        "price_rent": price_rent
    }
    response = requests.post(f"{BASE_URL}/addbook", json=data)
    return response.status_code, response.json()

# @app.get("/books")
# def route_booksearch():
#     data = request.get_json(silent = True) or {}   
#     title = data.get("title")
#     author = data.get("author")
#     books = booksearch(title=title, author=author)
#     return jsonify(ok=True, count=len(books), books=books)
def getbook(title = None, author = None):
    data = {
        "title":  title,
        "author": author}  
    response = requests.get(f"{BASE_URL}/books", json=data)
    
    try:
        data = response.json()  # Parse JSON data from the server
    except Exception:
        # If the server didn't return valid JSON
        return response.status_code, 0, []

    # Extract values safely
    count = data.get("count", 0)
    books = data.get("books", [])

    # Return (status code, number of books, book list)
    return response.status_code, count, books
        
    