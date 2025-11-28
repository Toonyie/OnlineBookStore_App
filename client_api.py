#Client Functions that the client_test.py and tinkter.py will use
import requests
BASE_URL = "http://127.0.0.1:5000"
session_token = None

#This is manly to get the get_token function on app.py to work
def auth_headers():
    if session_token:
        return {"Authorization": f"Bearer {session_token}"}
    return {}

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
    global session_token
    data = {
        "username": username,
        "password": password
    }
    response = requests.get(f"{BASE_URL}/loginaccount", json=data)
    result = response.json()
    
    #Generate a token if a user has been found and isn't already logged in
    if response.status_code == 200 and result.get("ok"):
        session_token = result.get("token")
        print("Saved session token:", session_token)

    return response.status_code, result

def logout():
    global session_token
    headers = {
        "Authorization": f"Bearer {session_token}"
    }
    resp = requests.get(f"{BASE_URL}/logout", headers=headers)
    session_token = None
    return resp.status_code, resp.json()

def addbook(title, author, price_buy, price_rent):
    data = {
        "title": title,
        "author": author,
        "price_buy": price_buy,
        "price_rent": price_rent
    }
    response = requests.post(
        f"{BASE_URL}/addbook", json=data, headers=auth_headers()
    )
    return response.status_code, response.json()

def getbook(title = None, author = None):
    data = {
        "title":  title,
        "author": author,
        }  
    
    response = requests.get(f"{BASE_URL}/books", json=data, headers=auth_headers())
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
        
def checkout(cart):
    if not session_token:
        return 401, {"ok": False, "message": "Not logged in"}
    data = {"cart": cart}
    resp = requests.post(f"{BASE_URL}/checkout",json=data,headers=auth_headers() 
    )
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, {
            "ok": False,
            "message": f"Server did not return JSON. Raw response:\n{resp.text}"
        }

