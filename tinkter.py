from tkinter import *
import tkinter as tk
from client_api import logout, login_account, create_account, getbook, checkout, view_orders, update_order_status,addbook
from tkinter import messagebox
from book_results import BookResults 
from email.message import EmailMessage
import threading

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


for frame in (menu_frame, create_frame, login_frame,customer_menu, book_search, shopping_cart, order_list, edit_books,manager_menu):
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
    def logout_task():
        try:
            logout()
            window.after(0, lambda: show_frame(menu_frame))
        except Exception as e:
            print("Logout error:", e)
            window.after(0, lambda: show_frame(menu_frame))
    threading.Thread(target=logout_task, daemon=True).start()

#Create account submit button helper function
def on_submit_create():
    username_input = username.get().strip()
    password_input = password.get().strip()
    email_input    = email.get().strip()
    admin_input = admin_password.get().strip()
    
    if not username_input or not password_input or not email_input:
        messagebox.showerror("Error", "Please fill in all fields.")
        return
    
    if "@" not in email_input or ".com" not in email_input:
        messagebox.showerror("Error", "Enter a valid email")
        return

    #Define the callback to run on Main Thread after network call
    def handle_create_response(status, data):
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

    def run_create_task():
        try:
            is_admin = (admin_input == "seal")
            status, data = create_account(username_input, email_input, password_input, not is_admin)
            window.after(0, handle_create_response, status, data)
        except Exception as e:
            window.after(0, lambda: messagebox.showerror("Error", f"Network error: {e}"))
    threading.Thread(target=run_create_task, daemon=True).start()
        
        
def handle_login_response(status, data, want_manager):
    if data.get("ok") and 200 <= status < 300:
        role = data.get("role")
        # Check if manager role is found
        if want_manager and role != "manager":
            messagebox.showerror("Error", "This account is not a manager.")
            return

        messagebox.showinfo("Success", data.get("message", "Login Successful!"))
        # Clear fields
        username.set("")
        password.set("")
        print(role)
        if role == "manager":
            show_frame(manager_menu)
        else:
            show_frame(customer_menu)
    else:
        message = data.get("message", "Login failed.")
        messagebox.showerror("Error", f"{message}\n(Status: {status})")


def login():
    # Get the user inputs from entry
    username_input = username.get().strip()
    password_input = password.get().strip()
    want_manager = is_manager_var.get()
    
    if not username_input or not password_input:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    # Define the background task
    def run_login_task():
        try:
            # This blocking call runs in the background
            status, data = login_account(username_input, password_input, want_manager)
            
            # Schedule UI update on main thread
            window.after(0, handle_login_response, status, data, want_manager)
        except Exception as e:
            window.after(0, lambda: messagebox.showerror("Error", f"Network error: {e}"))
    
    # Start the thread
    threading.Thread(target=run_login_task, daemon=True).start()
    
#Adding to card by book id and the order type
def add_to_cart(book, order_type):
    already_in_cart = sum(
        1 for item in cart if item["book_id"] == book["book_id"]
    )

    if already_in_cart >= book["quantity"]:
        messagebox.showwarning(
            "Out of stock",
            f'Sorry, only {book["quantity"]} copy/copies of "{book["title"]}" available.'
        )
        return

    cart.append({
        "book_id": book["book_id"],
        "title": book["title"],
        "author": book["author"],
        "price_buy": book["price_buy"],
        "price_rent": book["price_rent"],
        "type": order_type
    })

    refresh_cart()  #update cart UI whenever you add
    messagebox.showinfo("Cart", f'Added "{book["title"]}" to cart as {order_type}.')

    

def run_search():
    #Get inputs
    title_entry = title.get().strip()
    author_entry = author.get().strip()

    #Define callback
    def handle_search_response(status, count, books):
        if status == 200:
            results_widget.set_books(books)
            print("Found", count, "books")
        else:
            messagebox.showerror("Search failed", f"Status: {status}")

    #Define background task
    def search_task():
        try:
            status, count, books = getbook(title_entry, author_entry)
            window.after(0, handle_search_response, status, count, books)
        except Exception as e:
            window.after(0, lambda: messagebox.showerror("Error", f"Search error: {e}"))

    #Start Thread
    threading.Thread(target=search_task, daemon=True).start()


def on_checkout():
    #Check cart
    if not cart:
        messagebox.showwarning("Cart", "Cart is empty!")
        return

    #Define callback
    def handle_checkout_response(status, data):
        if status == 201 and data.get("ok"):
            messagebox.showinfo("Success", f'Order placed! Order ID: {data["order_id"]}')
            # It is safe to modify global cart here because we are back on main thread
            cart.clear()
            refresh_cart()
            show_frame(customer_menu)
        else:
            messagebox.showerror("Error", data.get("message", "Checkout failed"))

    #Define background task
    def checkout_task():
        try:
            status, data = checkout(list(cart)) 
            window.after(0, handle_checkout_response, status, data)
        except Exception as e:
            window.after(0, lambda: messagebox.showerror("Error", f"Checkout error: {e}"))

    #Start Thread
    threading.Thread(target=checkout_task, daemon=True).start()

#cart display
def refresh_cart():
    # clear old widgets
    for w in cart_list_frame.winfo_children():
        w.destroy()

    if not cart:
        tk.Label(cart_list_frame, text="Cart is empty.", bg="white",
                 font=("Arial", 12)).pack()
        return
    
    # group cart items by (book_id, type)
    grouped = {}
    for item in cart:
        key = (item["book_id"], item["type"])
        grouped[key] = grouped.get(key, 0) + 1
    grand_total = 0.0

    for (book_id, otype), qty in grouped.items():
        sample = next(
            i for i in cart
            if i["book_id"] == book_id and i["type"] == otype
        )

        unit_price = float(sample["price_buy"]) if otype == "buy" else float(sample["price_rent"])
        subtotal = unit_price * qty
        grand_total += subtotal  
        # Outer card for one cart item
        card = tk.Frame(cart_list_frame, bg="white", bd=1, relief="solid")
        card.pack(fill="x", padx=8, pady=6)

        # --- line 1: title + author
        tk.Label(
            card, text=sample["title"],
            bg="white", font=("Arial", 11, "bold"),
            anchor="w"
        ).pack(fill="x", padx=6, pady=(4, 0))

        tk.Label(
            card, text=f"by {sample['author']}",
            bg="white", font=("Arial", 10),
            anchor="w"
        ).pack(fill="x", padx=6)

        # --- line 2: compact details row
        details = tk.Frame(card, bg="white")
        details.pack(fill="x", padx=6, pady=4)

        tk.Label(details, text=otype.upper(), bg="white", width=6, anchor="w").grid(row=0, column=0, sticky="w")
        tk.Label(details, text=f"x{qty}", bg="white", width=4, anchor="w").grid(row=0, column=1, sticky="w")
        tk.Label(details, text=f"${unit_price:.2f} ea", bg="white", width=10, anchor="w").grid(row=0, column=2, sticky="w")
        tk.Label(details, text=f"= ${subtotal:.2f}", bg="white", width=10, anchor="w").grid(row=0, column=3, sticky="w")

        tk.Button(
            details, text="Remove 1",
            command=lambda bid=book_id, t=otype: remove_one(bid, t),
            width=8
        ).grid(row=0, column=4, padx=(10, 0), sticky="e")

        # make the prices stretch left nicely
        details.columnconfigure(3, weight=1)
        
    tk.Label(
        cart_list_frame,
        text=f"Order Total: ${grand_total:.2f}",
        bg="white",
        font=("Arial", 12, "bold"),
        anchor="e"
    ).pack(fill="x", padx=10, pady=(8, 0))

def remove_one(book_id, order_type):
    for i, item in enumerate(cart):
        if item["book_id"] == book_id and item["type"] == order_type:
            cart.pop(i)
            break
    refresh_cart()

#Helper for viewing orders UI
def refresh_orders():
    #Clear listbox immediately
    orders_listbox.delete(0, tk.END)

    #Define callback
    def handle_orders_response(status, orders):
        if status != 200:
            messagebox.showerror("Error", f"Failed to load orders (Status {status})")
            return

        # Save for selection lookup
        order_list.orders_cache = orders

        # Populate listbox
        for o in orders:
            orders_listbox.insert(
                tk.END,
                f'Order #{o["order_id"]} | User {o["user_id"]} | {o["status"]} | payed={o["payed"]} | {o["created_at"]}'
            )

    #Define background task
    def orders_task():
        try:
            status, orders = view_orders()
            window.after(0, handle_orders_response, status, orders)
        except Exception as e:
            window.after(0, lambda: messagebox.showerror("Error", f"Network error: {e}"))

    #Start Thread
    threading.Thread(target=orders_task, daemon=True).start()

def on_update_order():
    sel = orders_listbox.curselection()
    if not sel:
        messagebox.showwarning("Select order", "Please select an order first.")
        return

    idx = sel[0]

    if not hasattr(order_list, 'orders_cache'):
        return
        
    order = order_list.orders_cache[idx]
    order_id = order["order_id"]
    new_status = status_var.get()

    def handle_update_response(st, data):
        if st == 200 and data.get("ok"):
            messagebox.showinfo("Success", data.get("message", "Updated"))
            # Trigger refresh (which is also threaded now!)
            refresh_orders()
        else:
            messagebox.showerror("Error", data.get("message", f"Failed (Status {st})"))

    def update_task():
        try:
            st, data = update_order_status(order_id, new_status)
            window.after(0, handle_update_response, st, data)
        except Exception as e:
            window.after(0, lambda: messagebox.showerror("Error", f"Update error: {e}"))

    threading.Thread(target=update_task, daemon=True).start()

#Helper function to add/restock book 
def on_add_or_restock():
    #Get inputs
    title_val = m_title.get().strip()
    author_val = m_author.get().strip()
    buy_val = m_price_buy.get().strip()
    rent_val = m_price_rent.get().strip()
    qty_val = m_quantity.get().strip()

    if not title_val or not author_val or not buy_val or not rent_val or not qty_val:
        messagebox.showerror("Error", "Fill in all add/restock fields.")
        return
    
    try:
        qty_int = int(qty_val)
    except:
        messagebox.showerror("Error", "Quantity must be a number.")
        return

    #Define callback
    def handle_add_response(status, data):
        if status in (200, 201) and data.get("ok"):
            messagebox.showinfo("Success", data.get("message", "Book updated!"))
            # Clear fields
            m_title.set("")
            m_author.set("")
            m_price_buy.set("")
            m_price_rent.set("")
            m_quantity.set("")
        else:
            messagebox.showerror("Error", data.get("message", "Failed to add/restock."))

    #Define background task
    def add_task():
        try:
            status, data = addbook(title_val, author_val, buy_val, rent_val, qty_int)
            window.after(0, handle_add_response, status, data)
        except Exception as e:
            window.after(0, lambda: messagebox.showerror("Error", f"Add book error: {e}"))

    threading.Thread(target=add_task, daemon=True).start()
        
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

#Manager checkbox
is_manager_var = tk.BooleanVar(value=False)
tk.Checkbutton(loginform_frame,text="Login as manager",variable=is_manager_var,bg="lightblue").grid(row=2, column=0, columnspan=2, pady=8)

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
cart_list_frame = tk.Frame(shopping_cart, bg="white")
cart_list_frame.pack(pady=10, fill="both", expand=True)
Button(shopping_cart, text="Checkout", font=("Arial", 18), command= lambda:on_checkout()).pack(pady=10)
Back = Button(shopping_cart,text="Back", font=("Arial",25,), command = lambda:show_frame(customer_menu))
Back.pack(pady=10)




#Manager Menu
Label(manager_menu, text="Main Menu", bg = "white", font=("Arial", 25, "bold")).pack(pady=50)
option_frame2 = tk.Frame(manager_menu, bg="white")
option_frame2.pack(pady=10)  

View_Orders_button = Button(option_frame2, text="View Orders", font=("Arial",14), width = 20, height = 2, command = lambda: (show_frame(order_list), refresh_orders()))
edit_books_button = Button(option_frame2, text="Update Book Information", font=("Arial",14), width=20, height= 2, command=lambda:show_frame(edit_books))
logout_button = Button(option_frame2, text="Logout", font=("Arial",14), width=20, height = 2, command=lambda:logout_session())

View_Orders_button.grid(row=0, column=0, padx=5, pady=5)
edit_books_button.grid(row=1, column=0, padx=5, pady=5)
logout_button.grid(row=2, column=0, padx=5, pady=5)


#Orderbox UI
orders_listbox = tk.Listbox(order_list, width=70, height=12, font=("Arial", 11))
orders_listbox.pack(pady=10)
status_var = tk.StringVar(value="Pending Purchase Payment")
status_options = [
    "Pending Purchase Payment",
    "Pending Rental Payment",
    "Paid",
    "Delivered",
    "Returned",
    "Cancelled"
]
status_menu = tk.OptionMenu(order_list, status_var, *status_options)
status_menu.pack(pady=5)


Label(order_list, text= "All Orders").pack(pady=30)
tk.Button(order_list, text="Refresh Orders", font=("Arial", 12),
          command= lambda: refresh_orders()).pack(pady=5)

tk.Button(order_list, text="Update Selected Order", font=("Arial", 12),
          command=on_update_order).pack(pady=5)
Back = Button(order_list,text="Back", font=("Arial",25,), command = lambda:show_frame(manager_menu))
Back.pack(pady=10)


#Edit Books
Label(edit_books, text= "All Orders").pack(pady=30)
Label(edit_books, text="Update Book Information", bg="white",
      font=("Arial", 20, "bold")).pack(pady=15)

#Format to see the books in display
edit_form = tk.Frame(edit_books, bg="white")
edit_form.pack(pady=10)

# form variables
m_title = tk.StringVar()
m_author = tk.StringVar()
m_price_buy = tk.StringVar()
m_price_rent = tk.StringVar()
m_quantity = tk.StringVar()

# ---- Add / Restock book ----
tk.Label(edit_form, text="Title:", bg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
tk.Entry(edit_form, textvariable=m_title, width=25).grid(row=0, column=1, padx=5, pady=5)

tk.Label(edit_form, text="Author:", bg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
tk.Entry(edit_form, textvariable=m_author, width=25).grid(row=1, column=1, padx=5, pady=5)

tk.Label(edit_form, text="Buy Price:", bg="white").grid(row=2, column=0, sticky="e", padx=5, pady=5)
tk.Entry(edit_form, textvariable=m_price_buy, width=25).grid(row=2, column=1, padx=5, pady=5)

tk.Label(edit_form, text="Rent Price:", bg="white").grid(row=3, column=0, sticky="e", padx=5, pady=5)
tk.Entry(edit_form, textvariable=m_price_rent, width=25).grid(row=3, column=1, padx=5, pady=5)

tk.Label(edit_form, text="Quantity:", bg="white").grid(row=4, column=0, sticky="e", padx=5, pady=5)
tk.Entry(edit_form, textvariable=m_quantity, width=25).grid(row=4, column=1, padx=5, pady=5)

tk.Button(edit_books, text="Add / Restock Book",
          font=("Arial", 14), command=on_add_or_restock).pack(pady=10)
Back = Button(edit_books,text="Back", font=("Arial",25,), command = lambda:show_frame(manager_menu))
Back.pack(pady=10)


# Start on start page
show_frame(menu_frame)
window.mainloop()
