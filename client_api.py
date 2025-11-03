#Client Functions that the client_test.py and tinkter.py will use
import requests
BASE_URL = "http://127.0.0.1:5000"

def create_account(username, email, password, is_customer=True):
    data = {"username": username, "email": email, "password": password, "is_customer": is_customer}
    response = requests.post(f"{BASE_URL}/createaccount", json=data)
    return response.status_code, response.json()

