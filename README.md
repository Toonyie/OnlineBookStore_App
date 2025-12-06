# 🛒 Online Bookstore Desktop Application

## 📘 Project Overview
This project is a **desktop-based online bookstore system** built for a school assignment.  
It demonstrates full-stack fundamentals: database design, RESTful backend development, and a desktop GUI frontend.

### What users can do
- Create an account with **username, password, and email**
- Log in / log out
- Search books by **title and/or author**
- View results in a paginated list
- Add books to cart as **buy** or **rent**

### What managers can do
- Log in using a **manager account**
- View all orders in the system
- Update order status / payment status (e.g., Pending → Paid)
- Add new books or restock existing books by increasing quantity

The system is composed of:
- **Backend:** Python Flask REST API  
- **Database:** SQLite (`bookstore.db`)  
- **Frontend:** Python Tkinter desktop GUI  

---

## 🧩 Project Structure
The project consists of the following main files:

- **`app.py`**  
  Flask backend server. Implements RESTful API routes for:
  - account creation / login / logout (token-based sessions)
  - book searching
  - cart checkout and order creation
  - manager tools (view orders, update order status, add/restock books)

- **`client_api.py`**  
  Client-side API wrapper used by both CLI tests and the Tkinter GUI.  
  Handles:
  - making HTTP requests to the Flask server  
  - storing and attaching the session token  
  - helper functions like `login_account()`, `getbook()`, `checkout()`,  
    `view_orders()`, `update_order_status()`, etc.

- **`tinkter.py`**  
  Tkinter desktop application. Provides screens for:
  - main menu  
  - create account  
  - login (customer or manager)  
  - customer menu, book search results, shopping cart, checkout  
  - manager menu, order list, update status, add/restock books  

- **`book_results.py`**  
  UI helper class for displaying paginated book search results with Buy/Rent buttons.

- **`bookstore.db`**  
  SQLite database storing users, books, and orders (with quantities and statuses).

---
### 🗄️ Database Setup
1. **Install MySQL Server** and ensure the service is running.
2. **Import the Database:**
   - Open MySQL Workbench.
   - Go to **Server** > **Data Import**.
   - Select **Import from Self-Contained File** and choose the `database_setup.sql` file from this repository.
   - Click **Start Import**.
   *This will create the `bookstore_db` database and populate it with the required tables and sample data.*

---
### ⚙️ Configuration
1. Create a `.env` file in the root directory.
2. Copy the contents of `database.env.example` into `.env`.
3. Update `DB_PASS` with your local MySQL password.
## ▶️ How to Run
1. Start the backend server on a terminal:
   ```bash
   python app.py
2. Start the application on a seperate terminal:
   ```bash
   python tinkter.py

