#This file is mainly to give the search results after a user searches for a book
import tkinter as tk
from tkinter import ttk

PAGE_SIZE = 5
def ellipsize(text, max_chars=28):
    if text is None:
        return ""
    return text if len(text) <= max_chars else text[:max_chars-3] + "..."


class BookResults(ttk.Frame):
    def __init__(self, parent, add_to_cart_callback):
        super().__init__(parent)

        self.add_to_cart = add_to_cart_callback
        self.books = []
        self.page = 0

        self.results_box = ttk.Frame(self)
        self.results_box.pack(fill="both", expand=True)

        pager = ttk.Frame(self)
        pager.pack(pady=8)

        self.prev_btn = ttk.Button(pager, text="Prev", command=self.prev_page)
        self.prev_btn.grid(row=0, column=0, padx=5)

        self.page_lbl = ttk.Label(pager, text="Page 1")
        self.page_lbl.grid(row=0, column=1, padx=5)

        self.next_btn = ttk.Button(pager, text="Next", command=self.next_page)
        self.next_btn.grid(row=0, column=2, padx=5)

    def set_books(self, books):
        self.books = books or []
        self.page = 0
        self.render()

    def render(self):
        for w in self.results_box.winfo_children():
            w.destroy()

        start = self.page * PAGE_SIZE
        end = start + PAGE_SIZE
        visible = self.books[start:end]

        if not visible:
            ttk.Label(self.results_box, text="No results.").pack()
            self.page_lbl.config(text="Page 0")
            return

        for book in visible:
            row = ttk.Frame(self.results_box, padding=6)
            row.pack(fill="x", pady=2, padx=4)  

            row.columnconfigure(0, weight=2)  # title
            row.columnconfigure(1, weight=2)  # author
            row.columnconfigure(2, weight=0)  # buy label
            row.columnconfigure(3, weight=0)  # rent label
            row.columnconfigure(4, weight=0)  # buy button
            row.columnconfigure(5, weight=0)  # rent button
        
            title_text = ellipsize(book["title"], max_chars=28)
            ttk.Label(row, text=title_text, font=("Arial", 10, "bold"), width=30, anchor="w").grid(row=0, column=0, sticky="w")
            ttk.Label(row, text=book["author"], width=30, anchor="w").grid(row=0, column=1, sticky="w")
            ttk.Label(row, text=f'Buy: ${book["price_buy"]}').grid(row=0, column=2)
            ttk.Label(row, text=f'Rent: ${book["price_rent"]}').grid(row=0, column=3)

            ttk.Button(row, text="Buy",
                       command=lambda b=book: self.add_to_cart(b, "buy")
                      ).grid(row=0, column=4, padx=4)

            ttk.Button(row, text="Rent",
                       command=lambda b=book: self.add_to_cart(b, "rent")
                      ).grid(row=0, column=5, padx=4)

        total_pages = (len(self.books) - 1) // PAGE_SIZE + 1
        self.page_lbl.config(text=f"Page {self.page+1} / {total_pages}")

        self.prev_btn.config(state=("disabled" if self.page == 0 else "normal"))
        self.next_btn.config(state=("disabled" if self.page >= total_pages-1 else "normal"))

    def next_page(self):
        self.page += 1
        self.render()

    def prev_page(self):
        self.page -= 1
        self.render()
