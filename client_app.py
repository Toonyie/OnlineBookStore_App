# client.py
import requests

BASE_URL = "http://127.0.0.1:5000"  # change if your Flask runs on a different port

def main():
    print("=== Create Account Tester ===")
    print("Type 'quit' at any prompt to exit.\n")

    while True:
        username = input("Username: ").strip()
        if username.lower() == "quit": break
        email = input("Email: ").strip()
        if email.lower() == "quit": break
        password = input("Password: ").strip()
        if password.lower() == "quit": break
        role = input("Is customer? (true/false, default true): ").strip().lower()
        is_customer = (role != "false")

        payload = {
            "username": username,
            "email": email,
            "password": password,
            "is_customer": is_customer
        }

        try:
            resp = requests.post(f"{BASE_URL}/createaccount", json=payload, timeout=5)
            print(f"\nHTTP {resp.status_code}")
            print(resp.json())
        except requests.RequestException as e:
            print("Network error:", e)
        print()

    print("Goodbye!")

if __name__ == "__main__":
    main()
