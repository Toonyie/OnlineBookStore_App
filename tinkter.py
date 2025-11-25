from tkinter import *
import tkinter as tk
from client_api import logout, login_account, create_account, getbook
from tkinter import messagebox
from book_results import BookResults 

# widgets = GUI elements: buttons, textboxes, labels, etc
# windows = pop up that holds these widgets
window = Tk() #Create an instance of tk
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)

#Aesthetics of window
window.geometry("500x500")
window.title("Bookstore Application")
window.rowconfigure(0, weight=1)
window.columnconfigure(0, weight=1)
window.resizable(False, False) # no resizing in x or y

#Frames that switches
menu_frame   = tk.Frame(window, bg="beige")
create_frame = tk.Frame(window, bg="lightblue")
login_frame  = tk.Frame(window, bg="lightgreen")
customer_menu = tk.Frame(window, bg="white")
book_search = tk.Frame(window, bg="white")
shopping_cart = tk.Frame(window, bg="white")
manager_menu = tk.Frame(window, bg = "white")
order_list = tk.Frame(window, bg = "white")
edit_books = tk.Frame(window, bg="white")
cart = []  


for frame in (menu_frame, create_frame, login_frame,customer_menu, book_search, shopping_cart, order_list, edit_books):
    frame.grid(row=0, column=0, sticky="nsew")

Label(menu_frame, text="Welcome to the Bookstore!",
      font=("Arial", 25, "bold"), bg="beige").pack(pady=50)

#Just a helper function to show the frame when the corresponding button is clicked
def show_frame(frame):
    print(f"frame up,{frame}")
    frame.tkraise()

def quit_app():
    print("destroyed")
    window.destroy()

def back():
    show_frame(menu_frame)
    username.set("")
    password.set("")
    email.set("")
    admin_password.set("")
    title.set("")
    author.set("")


def logout_session():
    logout()
    show_frame(menu_frame)

#Create account submit button helper function
def on_submit_create():
    #Get the user inputs from entry
    username_input = username.get().strip()
    password_input = password.get().strip()
    email_input    = email.get().strip()
    admin_input = admin_password.get().strip()
    if not username or not password or not email:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    try:
        status, data = create_account(username_input, email_input, password_input, False if admin_input == "seal" else True)
    except Exception as e:
        messagebox.showerror("Error", f"Network error: {e}")
        return
    
    if data.get("ok") and 200 <= status < 300:
        messagebox.showinfo("Success", data.get("message", "Account created!"))
        # clear fields
        username.set("")
        password.set("")
        email.set("")
        show_frame(menu_frame)
    else:
        message = data.get("message", "Account creation failed.")
        messagebox.showerror("Error", f"{message}\n(Status: {status})")

def login():
    #Get the user inputs from entry
    username_input = username.get().strip()
    password_input = password.get().strip()

    if not username or not password:
        messagebox.showerror("Error", "Please fill in all fields.")
        return
    try:
        status, data = login_account(username_input, password_input)
    except Exception as e:
        messagebox.showerror("Error", f"Network error: {e}")
        return
    
    if data.get("ok") and 200 <= status < 300:
        messagebox.showinfo("Success", data.get("message", "Login Successful!"))
        # clear fields
        username.set("")
        password.set("")
        show_frame(customer_menu)
    else:
        message = data.get("message", "Login failed.")
        messagebox.showerror("Error", f"{message}\n(Status: {status})")

#Adding to card by book id and the order type


def add_to_cart(book, order_type):
    cart.append({"book_id": book["book_id"], "type": order_type})
    messagebox.showinfo("Cart", f'Added "{book["title"]}" to cart as {order_type}.')

def run_search():
    title_entry = title.get().strip()
    author_entry = author.get().strip()

    status, count, books = getbook(title_entry, author_entry)
    if status == 200:
        results_widget.set_books(books)  # ✅ push results into the widget
    else:
        print("Search failed", status)

#Main menu
create_account_button = Button(menu_frame, text="Create Account", font=("Arial",14), width = 20, height = 2, command = lambda:show_frame(create_frame))
create_account_button.pack(pady=20)

login_button = Button(menu_frame, text="Login", font=("Arial",14), width=20, height= 2, command=lambda:show_frame(login_frame))
login_button.pack(pady=20)

quit_button = Button(menu_frame, text="Quit", font=("Arial",14), width=20, height = 2, command=quit_app)
quit_button.pack(pady=20)



#Create_account_section
username = tk.StringVar()
password = tk.StringVar()
email = tk.StringVar()
admin_password = tk.StringVar()

Label(create_frame, text="Create Account",
      font=("Arial", 25, "bold"), bg="lightblue").pack(pady=30)

#Make a subframe called form_frame, mainly to prevent compilation error since create_frame spacing is controlled by pady
form_frame = tk.Frame(create_frame, bg="lightblue")
form_frame.pack(pady=10)

user_label = tk.Label(form_frame, text = "Username", font = ("Arial",10,"bold"))
user_input = Entry(form_frame, textvariable = username, font=("Arial",10))
password_label = tk.Label(form_frame, text = "Password", font = ("Arial",10,"bold"))
password_input = Entry(form_frame, textvariable = password, font=("Arial",10),show="*")
email_label = tk.Label(form_frame, text = "Email", font = ("Arial",10,"bold"))
email_input = Entry(form_frame, textvariable = email, font=("Arial",10))

user_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
user_input.grid(row=0, column=1, padx=5, pady=5)
password_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
password_input.grid(row=1, column=1, padx=5, pady=5)
email_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
email_input.grid(row=2, column=1, padx=5, pady=5)

Submit = Button(create_frame,text="Submit", font=("Arial",25,), command = lambda:on_submit_create())
Submit.pack()

Back = Button(create_frame,text="Back", font=("Arial",25,), command = lambda:back())
Back.pack(pady=10)



#Login section
Label(login_frame, text="Login Account",
      font=("Arial", 25, "bold")).pack(pady=30)

loginform_frame = tk.Frame(login_frame, bg="lightblue")
loginform_frame.pack(pady=10)

user_label = tk.Label(loginform_frame, text = "Username", font = ("Arial",10,"bold"))
user_input = Entry(loginform_frame, textvariable = username, font=("Arial",10))
password_label = tk.Label(loginform_frame, text = "Password", font = ("Arial",10,"bold"))
password_input = Entry(loginform_frame, textvariable = password, font=("Arial",10), show="*")
user_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
user_input.grid(row=0, column=1, padx=5, pady=5)
password_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
password_input.grid(row=1, column=1, padx=5, pady=5)

Login = Button(login_frame,text="Login", font=("Arial",25,), command = lambda:login())
Login.pack()
Back = Button(login_frame,text="Back", font=("Arial",25,), command = lambda:back())
Back.pack(pady=10)



#Customer Menu Screen
Label(customer_menu, text="Main Menu", bg = "white", font=("Arial", 25, "bold")).pack(pady=50)
option_frame = tk.Frame(customer_menu, bg="white")
option_frame.pack(pady=10)  

Booksearch_button = Button(option_frame, text="Booksearch", font=("Arial",14), width = 20, height = 2, command = lambda:show_frame(book_search))
Cart_button = Button(option_frame, text="Cart", font=("Arial",14), width=20, height= 2, command=lambda:show_frame(shopping_cart))
logout_button = Button(option_frame, text="Logout", font=("Arial",14), width=20, height = 2, command=lambda:logout_session())

Booksearch_button.grid(row=0, column=0, padx=5, pady=5)
Cart_button.grid(row=1, column=0, padx=5, pady=5)
logout_button.grid(row=2, column=0, padx=5, pady=5)




#Booksearch Screen
title = tk.StringVar()
author = tk.StringVar()


Label(book_search, text="Search books!", bg="white", font=("Arial", 25, "bold")).pack(pady=10)
Label(book_search, text="Search Book with Title and/or Author", bg="white", font=("Arial", 10, "bold")).pack(pady=10)
option_frame1 = tk.Frame(book_search)
option_frame1.pack(pady=10)  
Title_label = tk.Label(option_frame1, text = "Title", font = ("Arial",10,"bold"))
Title_input = Entry(option_frame1, textvariable = title, font=("Arial",10))
Author_label = tk.Label(option_frame1, text = "Author", font = ("Arial",10,"bold"))
Author_input = Entry(option_frame1, textvariable = author, font=("Arial",10))

Search = Button(book_search,text="Search", font=("Arial",25,), command = lambda:run_search())
Search.pack(pady=8)

results_widget = BookResults(book_search, add_to_cart)
results_widget.pack(pady=5, fill="x")   # smaller + centered

Back = Button(book_search,text="Back", font=("Arial",25,), command = lambda:show_frame(customer_menu))
Back.pack(pady=10)

Title_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
Title_input.grid(row=0, column=1, padx=5, pady=5)
Author_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
Author_input.grid(row=1, column=1, padx=5, pady=5)




#ShoppingCart

Label(shopping_cart, text= "Cart").pack(pady=30)
Back = Button(shopping_cart,text="Back", font=("Arial",25,), command = lambda:show_frame(customer_menu))
Back.pack(pady=10)



# Start on start page
show_frame(menu_frame)
window.mainloop()
