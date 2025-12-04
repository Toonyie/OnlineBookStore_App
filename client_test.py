from client_api import (
    create_account, login_account, logout,
    addbook, getbook, auth_headers
)
import client_api  #client_api.session_token

if __name__ == "__main__":
    print("Type: create | login | login_manager | logout | whoami | addbook | searchbook | quit")

    while True:
        #show session persistence here
        if client_api.session_token:
            print(f"\n✅ Logged in. Token (short): {client_api.session_token[:8]}...")
        else:
            print("\n❌ Not logged in.")
        print("--------------------------------------------------")

        cmd = input("Command: ").strip().lower()

        if cmd == "quit":
            break

        elif cmd == "create":
            u = input("Username: ").strip()
            e = input("Email: ").strip()
            p = input("Password: ").strip()
            owners_answer = input("What is the owner's favorite animal: ").strip()

            if owners_answer == "seal":
                status, data = create_account(u, e, p, False)
            else:
                status, data = create_account(u, e, p)

            print(f"Status: {status}\nResponse: {data}\n")

        elif cmd == "login":
            u = input("Username: ").strip()
            p = input("Password: ").strip()

            status, data = login_account(u, p, want_manager=False)
            print(f"Status: {status}\nResponse: {data}\n")

            # show that token is stored
            print("Saved token now:", client_api.session_token)

        elif cmd == "login_manager":
            u = input("Username: ").strip()
            p = input("Password: ").strip()

            status, data = login_account(u, p, want_manager=True)
            print(f"Status: {status}\nResponse: {data}\n")

            print("Saved token now:", client_api.session_token)

        elif cmd == "logout":
            status, data = logout()
            print(f"Status: {status}\nResponse: {data}\n")
            print("Token after logout:", client_api.session_token)

        elif cmd == "whoami":
            # just reveal what session we have
            if not client_api.session_token:
                print("Not logged in.\n")
            else:
                print("Currently logged in.")
                print("Authorization headers that will be sent:")
                print(auth_headers(), "\n")

        elif cmd == "addbook":
            t = input("Title: ").strip()
            a = input("Author: ").strip()
            b = input("Buying Price: ").strip()
            r = input("Renting Price: ").strip()
            q = input("Quantity (default 1): ").strip() or "1"

            status, data = addbook(t, a, b, r, q)
            print(f"Status: {status}\nResponse: {data}\n")

        elif cmd == "searchbook":
            t = input("Title (or blank): ").strip()
            a = input("Author (or blank): ").strip()

            status, num_books, books = getbook(t or None, a or None)
            print(f"Status: {status}\nNumber of Books: {num_books}\n")

            for i, b in enumerate(books, start=1):
                print(f"{i}. {b['title']} — {b['author']}")
                print(f"   💰 Buy: ${float(b['price_buy']):.2f} | 💸 Rent: ${float(b['price_rent']):.2f}")
                print(f"   📦 Qty: {b.get('quantity', '?')}")
                print("-" * 50)

        else:
            print("Invalid Input, Try again!")
