from client_api import create_account,login_account, logout, addbook,getbook
if __name__ == "__main__":
    print("Type: create | login | logout | quit")

    while True:
        cmd = input("Command: ").strip().lower()

        if cmd == "quit":
            break

        elif cmd == "create":
            u = input("Username: ").strip()
            e = input("Email: ").strip()
            p = input("Password: ").strip()
            status, data = create_account(u, e, p)
            print(f"Status: {status}\nResponse: {data}\n")

        elif cmd == "login":
            u = input("Username: ").strip()
            p = input("Password: ").strip()
            status, data = login_account(u, p)
            print(f"Status: {status}\nResponse: {data}\n")

        elif cmd == "logout":
            status, data = logout()
            print(f"Status: {status}\nResponse: {data}\n")
        
        elif cmd == "addbook":
            t = input("Title: ").strip()
            a = input("Author: ").strip()
            b = input("Buying Price: ")
            r = input("Renting Price: ")
            status,data = addbook(t, a, b, r)
            print(f"Status: {status}\nResponse: {data}\n")
        
        elif cmd == "searchbook":
            t = input("Title: ").strip()
            a = input("Author: ").strip()
            status,num_books, books = getbook(t,a)
            print(f"Status: {status}\nNumber of Books: {num_books}\nResponse: {books}\n")

            for i, b in enumerate(books, start=1):
                print(f"{i}. {b['title']} — {b['author']}")
                print(f"   💰 Buy: ${b['price_buy']:.2f} | 💸 Rent: ${b['price_rent']:.2f}")
                print(f"   📖 Active: {'Yes' if b['active'] else 'No'}")
                print("-" * 50)

        else:
            print("Invalid Input, Try again!")
    
