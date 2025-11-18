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


title_label = Label(window,text="Welcome to the Bookstore!",font=("Arial", 25, "bold"),bg="beige")
title_label.pack(pady=50)

#Frames that switches
menu_frame   = tk.Frame(window, bg="beige")
create_frame = tk.Frame(window, bg="lightblue")
login_frame  = tk.Frame(window, bg="lightgreen")

for frame in (menu_frame, create_frame, login_frame):
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

#Home Screen
create_account_button = Button(menu_frame, text="Create Account", font=("Arial",14), width = 20, height = 2, command = lambda:show_frame(create_frame))
create_account_button.pack(pady=20)

login_button = Button(menu_frame, text="Login", font=("Arial",14), width=20, height= 2, command=lambda:show_frame(login_frame))
login_button.pack(pady=20)

quit_button = Button(menu_frame, text="Quit", font=("Arial",14), width=20, height = 2, command=quit_app)
quit_button.pack(pady=20)



# Start on main menu
show_frame(menu_frame)

window.mainloop()
