from client_api import create_account,login_account, logout
if __name__ == "__main__":
    print("Type: create | login | logout | quit")

    while True:
        cmd = input("Command: ").strip().lower()

        if cmd == "quit":
            break

        elif cmd == "create":
            u = input("Username: ")
            e = input("Email: ")
            p = input("Password: ")
            status, data = create_account(u, e, p)
            print(f"Status: {status}\nResponse: {data}\n")

        elif cmd == "login":
            u = input("Username: ")
            p = input("Password: ")
            status, data = login_account(u, p)
            print(f"Status: {status}\nResponse: {data}\n")

        elif cmd == "logout":
            status, data = logout()
            print(f"Status: {status}\nResponse: {data}\n")
    
