from client_api import create_account

def main():
    print("=== CLI Tester ===")
    u = input("Username: ")
    e = input("Email: ")
    p = input("Password: ")
    s, resp = create_account(u, e, p)
    print(s, resp)

if __name__ == "__main__":
    main()
