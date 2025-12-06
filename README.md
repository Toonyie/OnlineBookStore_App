# 🛒 Online Bookstore Desktop Application

## 📘 Project Overview
This project is a **desktop-based online bookstore system** built for a school assignment.  
It demonstrates full-stack fundamentals: relational database design, RESTful backend development, and a desktop GUI frontend.

### What users can do
- Create an account with **username, password, and email**
- Log in / log out
- Search books by **title and/or author**
- View results in a paginated list
- Add books to cart as **buy** or **rent**
- **Receive email receipts** upon checkout

### What managers can do
- Log in using a **manager account**
- View all orders in the system
- Update order status / payment status (e.g., Pending → Paid)
- Add new books or restock existing books by increasing quantity

The system is composed of:
- **Backend:** Python Flask REST API  
- **Database:** MySQL Server (v8.0+)  
- **Frontend:** Python Tkinter desktop GUI (Asynchronous & Threaded)

---

## 🧩 Project Structure
The project consists of the following main files:

- **`app.py`** Flask backend server. Implements RESTful API routes using **Connection Pooling** for performance.
  - account creation / login / logout (token-based sessions)
  - book searching
  - cart checkout and order creation
  - manager tools (view orders, update order status, add/restock books)

- **`client_api.py`** Client-side API wrapper used by both CLI tests and the Tkinter GUI.  
  Handles:
  - making HTTP requests to the Flask server  
  - storing and attaching the session token  
  - helper functions like `login_account()`, `getbook()`, `checkout()`, etc.

- **`tinkter.py`** Tkinter desktop application. Provides screens for all user interactions.
  - **Note:** Uses Python `threading` to ensure the GUI remains responsive during network calls.

- **`database_setup.sql`** SQL dump file containing the database schema and sample data required to run the app.

- **`database.env`** Configuration file for environment variables (Database credentials & Email config). **(Not included in repo for security)**

---

## ⚙️ Setup & Configuration
Before running the application, you must configure the database and email settings.

### 1. Database Setup
1. **Install MySQL Server** and ensure the service is running on port `3306`.
2. **Import the Database:**
   - Open **MySQL Workbench**.
   - Go to **Server** > **Data Import**.
   - Select **Import from Self-Contained File** and choose the `database_setup.sql` file from this repository.
   - Click **Start Import**.
   *This will create the `bookstore_db` database and populate it with the required tables.*

### 2. Configuration File (`database.env`)
You need to create a configuration file to store your secrets.

1. Create a file named **`database.env`** in the root directory.
2. Copy the template below and fill in your details:

   ```ini
   # Database Config
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=bookstore_db
   DB_USER=your_mysql_user      # e.g., bookstore_admin
   DB_PASS=your_mysql_password
   
   # Email Config (Required for Billing Receipts)
   BOOKSTORE_EMAIL=your_email@gmail.com
   BOOKSTORE_EMAIL_PASS=abcdefghijklmnop

## ▶️ How to Run
Open a terminal in the project folder and run:
```bash
pip install -r requirements.txt
python app.py
```
On a seperate terminal run:
```bash
python tinkter.py
```
