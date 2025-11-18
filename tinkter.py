from tkinter import *
import tkinter as tk
from client_api import create_account, login_account
from tkinter import messagebox

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

#Frames that switches
menu_frame   = tk.Frame(window, bg="beige")
create_frame = tk.Frame(window, bg="lightblue")
login_frame  = tk.Frame(window, bg="lightgreen")
main_menu = tk.Frame(window, bg="white")

for frame in (menu_frame, create_frame, login_frame,main_menu):
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

#Create account submit button helper function
def on_submit_create():
    #Get the user inputs from entry
    username_input = username.get().strip()
    password_input = password.get().strip()
    email_input    = email.get().strip()

    if not username or not password or not email:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    try:
        status, data = create_account(username_input, email_input, password_input, True)
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
        show_frame(main_menu)
    else:
        message = data.get("message", "Login failed.")
        messagebox.showerror("Error", f"{message}\n(Status: {status})")


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

Back = Button(create_frame,text="Back", font=("Arial",25,), command = lambda:show_frame(menu_frame))
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
Back = Button(login_frame,text="Back", font=("Arial",25,), command = lambda:show_frame(menu_frame))
Back.pack(pady=10)

# Start on main menu
show_frame(menu_frame)
window.mainloop()
