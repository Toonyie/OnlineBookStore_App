import threading
import tkinter as tk
from tkinter import messagebox
from client_test import create_account

class CreateAccountApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Create Account")
        self.geometry("320x220")

        tk.Label(self, text="Username").pack(anchor="w", padx=12, pady=(12,0))
        self.username = tk.Entry(self); self.username.pack(fill="x", padx=12)

        tk.Label(self, text="Email").pack(anchor="w", padx=12, pady=(8,0))
        self.email = tk.Entry(self); self.email.pack(fill="x", padx=12)

        tk.Label(self, text="Password").pack(anchor="w", padx=12, pady=(8,0))
        self.password = tk.Entry(self, show="*"); self.password.pack(fill="x", padx=12)

        self.is_customer = tk.BooleanVar(value=True)
        tk.Checkbutton(self, text="Is customer", variable=self.is_customer).pack(anchor="w", padx=12, pady=8)

        self.btn = tk.Button(self, text="Create Account", command=self.on_submit)
        self.btn.pack(pady=10)

        self.status = tk.Label(self, text="", fg="gray")
        self.status.pack(pady=(0,12))

    def on_submit(self):
        u = self.username.get().strip()
        e = self.email.get().strip()
        p = self.password.get().strip()
        ic = self.is_customer.get()

        if not u or not e or not p:
            messagebox.showwarning("Missing fields", "Please fill username, email, and password.")
            return

        self.btn.config(state="disabled")
        self.status.config(text="Creating account...")

        def work():
            try:
                data = create_account(u, e, p, ic)
                self.after(0, lambda: (
                    messagebox.showinfo("Success", data.get("message","Account created")),
                    self.status.config(text="Done"),
                    self.btn.config(state="normal"),
                ))
            except Exception as ex:
                self.after(0, lambda: (
                    messagebox.showerror("Error", str(ex)),
                    self.status.config(text="Failed"),
                    self.btn.config(state="normal"),
                ))

        threading.Thread(target=work, daemon=True).start()

if __name__ == "__main__":
    CreateAccountApp().mainloop()
