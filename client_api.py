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