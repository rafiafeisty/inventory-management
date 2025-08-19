import sqlite3
import hashlib
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Product:
    def __init__(self, product_id=None, product_name="", product_price=0.0):
        self.product_id = product_id
        self.product_name = product_name
        self.product_price = product_price

class ProductManager:
    def __init__(self):
        self.conn = sqlite3.connect("inventory.db")
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            product_price REAL NOT NULL CHECK(product_price > 0)
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS stocks (
            stock_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            stock_quantity INTEGER NOT NULL CHECK(stock_quantity >= 0),
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        )
        """)
        self.conn.commit()

    def add_product(self, product_name, product_price):
        try:
            product_price = float(product_price)
            if product_price <= 0:
                return False, "Price must be positive"
            self.cursor.execute(
                "INSERT INTO products (product_name, product_price) VALUES (?, ?)",
                (product_name, product_price)
            )
            self.conn.commit()
            return True, f"Product added successfully with ID: {self.cursor.lastrowid}"
        except ValueError:
            return False, "Invalid price. Please enter a number"
        except sqlite3.Error as e:
            return False, f"Error adding product: {e}"

    def delete_product(self, pid):
        try:
            self.cursor.execute("SELECT 1 FROM products WHERE product_id=?", (pid,))
            if not self.cursor.fetchone():
                return False, "No such product found"
            self.cursor.execute("DELETE FROM products WHERE product_id=?", (pid,))
            self.conn.commit()
            return True, "Product deleted successfully"
        except sqlite3.Error as e:
            return False, f"Error deleting product: {e}"

    def edit_product(self, pid, product_name, product_price):
        try:
            product_price = float(product_price)
            if product_price <= 0:
                return False, "Price must be positive"
            self.cursor.execute("SELECT * FROM products WHERE product_id=?", (pid,))
            if not self.cursor.fetchone():
                return False, "No such product found"
            self.cursor.execute(
                "UPDATE products SET product_name=?, product_price=? WHERE product_id=?",
                (product_name, product_price, pid)
            )
            self.conn.commit()
            return True, "Product updated successfully"
        except ValueError:
            return False, "Invalid price. Please enter a number"
        except sqlite3.Error as e:
            return False, f"Error updating product: {e}"

    def get_all_products(self):
        self.cursor.execute("SELECT * FROM products")
        return self.cursor.fetchall()

class StockManager:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()

    def add_stock(self, pid, quantity):
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return False, "Quantity must be positive"
            self.cursor.execute("SELECT 1 FROM products WHERE product_id=?", (pid,))
            if not self.cursor.fetchone():
                return False, "No such product ID exists"
            self.cursor.execute(
                "INSERT INTO stocks (product_id, stock_quantity) VALUES (?, ?)",
                (pid, quantity)
            )
            self.conn.commit()
            return True, f"Stock added successfully! Stock ID: {self.cursor.lastrowid}"
        except ValueError:
            return False, "Invalid input. Please enter numbers"
        except sqlite3.Error as e:
            return False, f"Error adding stock: {e}"

    def edit_stock(self, sid, quantity):
        try:
            quantity = int(quantity)
            if quantity < 0:
                return False, "Quantity cannot be negative"
            self.cursor.execute("SELECT * FROM stocks WHERE stock_id=?", (sid,))
            if not self.cursor.fetchone():
                return False, "No such stock ID exists"
            self.cursor.execute(
                "UPDATE stocks SET stock_quantity=? WHERE stock_id=?",
                (quantity, sid)
            )
            self.conn.commit()
            return True, "Stock updated successfully!"
        except ValueError:
            return False, "Invalid input"
        except sqlite3.Error as e:
            return False, f"Error updating stock: {e}"

    def delete_stock(self, sid):
        try:
            self.cursor.execute("SELECT 1 FROM stocks WHERE stock_id=?", (sid,))
            if not self.cursor.fetchone():
                return False, "No such stock ID exists"
            self.cursor.execute("DELETE FROM stocks WHERE stock_id=?", (sid,))
            self.conn.commit()
            return True, "Stock deleted successfully!"
        except sqlite3.Error as e:
            return False, f"Error deleting stock: {e}"

    def get_all_stocks(self):
        self.cursor.execute("""
        SELECT s.stock_id, p.product_id, p.product_name, s.stock_quantity 
        FROM stocks s
        JOIN products p ON s.product_id = p.product_id
        """)
        return self.cursor.fetchall()

class Supplier:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            supplier_name TEXT NOT NULL,
            FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
        )
        """)
        self.conn.commit()

    def add_supplier(self, pid, supplier_name):
        try:
            self.cursor.execute("SELECT 1 FROM products WHERE product_id=?", (pid,))
            if not self.cursor.fetchone():
                return False, "No such product id exists"
            self.cursor.execute(
                "INSERT INTO suppliers (product_id, supplier_name) VALUES (?, ?)",
                (pid, supplier_name)
            )
            self.conn.commit()
            return True, "Supplier added successfully"
        except sqlite3.Error as e:
            return False, f"Error adding supplier: {e}"

    def edit_supplier(self, sid, pid, supplier_name):
        try:
            self.cursor.execute("SELECT 1 FROM suppliers WHERE supplier_id=?", (sid,))
            if not self.cursor.fetchone():
                return False, "No such supplier ID exists"
            self.cursor.execute("SELECT 1 FROM products WHERE product_id=?", (pid,))
            if not self.cursor.fetchone():
                return False, "No such product id exists"
            self.cursor.execute(
                "UPDATE suppliers SET product_id=?, supplier_name=? WHERE supplier_id=?",
                (pid, supplier_name, sid)
            )
            self.conn.commit()
            return True, "Supplier updated successfully"
        except sqlite3.Error as e:
            return False, f"Error updating supplier: {e}"

    def delete_supplier(self, sid):
        try:
            self.cursor.execute("SELECT 1 FROM suppliers WHERE supplier_id=?", (sid,))
            if not self.cursor.fetchone():
                return False, "No such supplier ID exists"
            self.cursor.execute("DELETE FROM suppliers WHERE supplier_id=?", (sid,))
            self.conn.commit()
            return True, "Supplier deleted successfully"
        except sqlite3.Error as e:
            return False, f"Error deleting supplier: {e}"

    def get_all_suppliers(self):
        self.cursor.execute("""
        SELECT s.supplier_id, p.product_id, p.product_name, s.supplier_name 
        FROM suppliers s
        JOIN products p ON s.product_id = p.product_id
        """)
        return self.cursor.fetchall()

class Sale:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
            stock_id INTEGER NOT NULL,
            amount_sold INTEGER NOT NULL,
            FOREIGN KEY (stock_id) REFERENCES stocks(stock_id) ON DELETE CASCADE
        )
        """)
        self.conn.commit()

    def add_sale(self, sid, amount):
        try:
            amount = int(amount)
            if amount <= 0:
                return False, "Amount must be positive"
            self.cursor.execute("SELECT 1 FROM stocks WHERE stock_id=?", (sid,))
            if not self.cursor.fetchone():
                return False, "No such stock id exists"
            self.cursor.execute(
                "INSERT INTO sales (stock_id, amount_sold) VALUES (?, ?)",
                (sid, amount)
            )
            self.conn.commit()
            return True, "Sale added successfully"
        except sqlite3.Error as e:
            return False, f"Error adding sale: {e}"

    def edit_sale(self, sid, amount):
        try:
            amount = int(amount)
            if amount <= 0:
                return False, "Amount must be positive"
            self.cursor.execute("SELECT 1 FROM sales WHERE sale_id=?", (sid,))
            if not self.cursor.fetchone():
                return False, "No such sale id exists"
            self.cursor.execute(
                "UPDATE sales SET amount_sold=? WHERE sale_id=?",
                (amount, sid)
            )
            self.conn.commit()
            return True, "Sale updated successfully"
        except sqlite3.Error as e:
            return False, f"Error updating sale: {e}"

    def delete_sale(self, sid):
        try:
            self.cursor.execute("SELECT 1 FROM sales WHERE sale_id=?", (sid,))
            if not self.cursor.fetchone():
                return False, "No such sale id exists"
            self.cursor.execute("DELETE FROM sales WHERE sale_id=?", (sid,))
            self.conn.commit()
            return True, "Sale deleted successfully"
        except sqlite3.Error as e:
            return False, f"Error deleting sale: {e}"

    def get_all_sales(self):
        self.cursor.execute("""
        SELECT s.sale_id, st.stock_id, p.product_name, s.amount_sold 
        FROM sales s
        JOIN stocks st ON s.stock_id = st.stock_id
        JOIN products p ON st.product_id = p.product_id
        """)
        return self.cursor.fetchall()

class Authentication:
    def __init__(self, conn):
        self.conn = conn
        self.cursor = conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS authentication (
            admin_id TEXT PRIMARY KEY,
            password TEXT
        )
        """)
        self.conn.commit()

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def add_admin(self, admin_id, password):
        hashed_password = self._hash_password(password)
        try:
            self.cursor.execute(
                "INSERT INTO authentication (admin_id, password) VALUES (?, ?)",
                (admin_id, hashed_password)
            )
            self.conn.commit()
            return True, "Admin created successfully"
        except sqlite3.IntegrityError:
            return False, "Username already exists"

    def login(self, admin_id, password):
        hashed_password = self._hash_password(password)
        self.cursor.execute(
            "SELECT 1 FROM authentication WHERE admin_id=? AND password=?",
            (admin_id, hashed_password)
        )
        result = self.cursor.fetchone()
        return bool(result), "Successfully logged in" if result else "Invalid credentials"

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Product Management System")
        self.pm = ProductManager()
        self.supplier_manager = Supplier(self.pm.conn)
        self.sale_manager = Sale(self.pm.conn)
        self.auth = Authentication(self.pm.conn)
        self.create_login_window()

    def create_login_window(self):
        self.clear_window()
        tk.Label(self.root, text="Product Management System", font=("Arial", 16)).pack(pady=10)
        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        tk.Button(self.root, text="Login", command=self.handle_login).pack(pady=10)
        tk.Button(self.root, text="Create Admin", command=self.handle_create_admin).pack()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = self.auth.login(username, password)
        messagebox.showinfo("Login", message)
        if success:
            self.create_main_menu()
        else:
            self.create_login_window()

    def handle_create_admin(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, message = self.auth.add_admin(username, password)
        messagebox.showinfo("Create Admin", message)

    def create_main_menu(self):
        self.clear_window()
        tk.Label(self.root, text="Product Management System", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Product Management", command=self.product_management).pack(pady=5)
        tk.Button(self.root, text="Stock Management", command=self.stock_management).pack(pady=5)
        tk.Button(self.root, text="Supplier Management", command=self.supplier_management).pack(pady=5)
        tk.Button(self.root, text="Sales Management", command=self.sales_management).pack(pady=5)
        tk.Button(self.root, text="Generate Reports", command=self.generate_reports).pack(pady=5)
        tk.Button(self.root, text="Exit", command=self.root.quit).pack(pady=5)

    def product_management(self):
        self.clear_window()
        tk.Label(self.root, text="Product Management", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Add Product", command=self.add_product_ui).pack(pady=5)
        tk.Button(self.root, text="Edit Product", command=self.edit_product_ui).pack(pady=5)
        tk.Button(self.root, text="Delete Product", command=self.delete_product_ui).pack(pady=5)
        tk.Button(self.root, text="View All Products", command=self.view_all_products).pack(pady=5)
        tk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu).pack(pady=5)

    def add_product_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Add Product", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Product Name:").pack()
        name_entry = tk.Entry(self.root)
        name_entry.pack()
        tk.Label(self.root, text="Product Price:").pack()
        price_entry = tk.Entry(self.root)
        price_entry.pack()
        tk.Button(self.root, text="Add", command=lambda: self.handle_add_product(name_entry.get(), price_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.product_management).pack(pady=5)

    def handle_add_product(self, name, price):
        success, message = self.pm.add_product(name, price)
        messagebox.showinfo("Add Product", message)
        if success:
            self.product_management()

    def edit_product_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Edit Product", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Product ID:").pack()
        pid_entry = tk.Entry(self.root)
        pid_entry.pack()
        tk.Label(self.root, text="New Product Name:").pack()
        name_entry = tk.Entry(self.root)
        name_entry.pack()
        tk.Label(self.root, text="New Product Price:").pack()
        price_entry = tk.Entry(self.root)
        price_entry.pack()
        tk.Button(self.root, text="Update", command=lambda: self.handle_edit_product(pid_entry.get(), name_entry.get(), price_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.product_management).pack(pady=5)

    def handle_edit_product(self, pid, name, price):
        try:
            pid = int(pid)
            success, message = self.pm.edit_product(pid, name, price)
            messagebox.showinfo("Edit Product", message)
            if success:
                self.product_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid product ID")

    def delete_product_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Delete Product", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Product ID:").pack()
        pid_entry = tk.Entry(self.root)
        pid_entry.pack()
        tk.Button(self.root, text="Delete", command=lambda: self.handle_delete_product(pid_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.product_management).pack(pady=5)

    def handle_delete_product(self, pid):
        try:
            pid = int(pid)
            success, message = self.pm.delete_product(pid)
            messagebox.showinfo("Delete Product", message)
            if success:
                self.product_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid product ID")

    def view_all_products(self):
        self.clear_window()
        tk.Label(self.root, text="All Products", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(self.root, columns=("ID", "Name", "Price"), show="headings")
        tree.heading("ID", text="Product ID")
        tree.heading("Name", text="Product Name")
        tree.heading("Price", text="Price")
        tree.pack(fill="both", expand=True)
        for product in self.pm.get_all_products():
            tree.insert("", "end", values=product)
        tk.Button(self.root, text="Back", command=self.product_management).pack(pady=5)

    def stock_management(self):
        self.clear_window()
        tk.Label(self.root, text="Stock Management", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Add Stock", command=self.add_stock_ui).pack(pady=5)
        tk.Button(self.root, text="Edit Stock", command=self.edit_stock_ui).pack(pady=5)
        tk.Button(self.root, text="Delete Stock", command=self.delete_stock_ui).pack(pady=5)
        tk.Button(self.root, text="View All Stocks", command=self.view_all_stocks).pack(pady=5)
        tk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu).pack(pady=5)

    def add_stock_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Add Stock", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Product ID:").pack()
        pid_entry = tk.Entry(self.root)
        pid_entry.pack()
        tk.Label(self.root, text="Quantity:").pack()
        quantity_entry = tk.Entry(self.root)
        quantity_entry.pack()
        tk.Button(self.root, text="Add", command=lambda: self.handle_add_stock(pid_entry.get(), quantity_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.stock_management).pack(pady=5)

    def handle_add_stock(self, pid, quantity):
        try:
            pid = int(pid)
            success, message = StockManager(self.pm.conn).add_stock(pid, quantity)
            messagebox.showinfo("Add Stock", message)
            if success:
                self.stock_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid input")

    def edit_stock_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Edit Stock", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Stock ID:").pack()
        sid_entry = tk.Entry(self.root)
        sid_entry.pack()
        tk.Label(self.root, text="New Quantity:").pack()
        quantity_entry = tk.Entry(self.root)
        quantity_entry.pack()
        tk.Button(self.root, text="Update", command=lambda: self.handle_edit_stock(sid_entry.get(), quantity_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.stock_management).pack(pady=5)

    def handle_edit_stock(self, sid, quantity):
        try:
            sid = int(sid)
            success, message = StockManager(self.pm.conn).edit_stock(sid, quantity)
            messagebox.showinfo("Edit Stock", message)
            if success:
                self.stock_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid input")

    def delete_stock_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Delete Stock", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Stock ID:").pack()
        sid_entry = tk.Entry(self.root)
        sid_entry.pack()
        tk.Button(self.root, text="Delete", command=lambda: self.handle_delete_stock(sid_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.stock_management).pack(pady=5)

    def handle_delete_stock(self, sid):
        try:
            sid = int(sid)
            success, message = StockManager(self.pm.conn).delete_stock(sid)
            messagebox.showinfo("Delete Stock", message)
            if success:
                self.stock_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid stock ID")

    def view_all_stocks(self):
        self.clear_window()
        tk.Label(self.root, text="All Stocks", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(self.root, columns=("Stock ID", "Product ID", "Product Name", "Quantity"), show="headings")
        tree.heading("Stock ID", text="Stock ID")
        tree.heading("Product ID", text="Product ID")
        tree.heading("Product Name", text="Product Name")
        tree.heading("Quantity", text="Quantity")
        tree.pack(fill="both", expand=True)
        for stock in StockManager(self.pm.conn).get_all_stocks():
            tree.insert("", "end", values=stock)
        tk.Button(self.root, text="Back", command=self.stock_management).pack(pady=5)

    def supplier_management(self):
        self.clear_window()
        tk.Label(self.root, text="Supplier Management", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Add Supplier", command=self.add_supplier_ui).pack(pady=5)
        tk.Button(self.root, text="Edit Supplier", command=self.edit_supplier_ui).pack(pady=5)
        tk.Button(self.root, text="Delete Supplier", command=self.delete_supplier_ui).pack(pady=5)
        tk.Button(self.root, text="View All Suppliers", command=self.view_all_suppliers).pack(pady=5)
        tk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu).pack(pady=5)

    def add_supplier_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Add Supplier", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Product ID:").pack()
        pid_entry = tk.Entry(self.root)
        pid_entry.pack()
        tk.Label(self.root, text="Supplier Name:").pack()
        name_entry = tk.Entry(self.root)
        name_entry.pack()
        tk.Button(self.root, text="Add", command=lambda: self.handle_add_supplier(pid_entry.get(), name_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.supplier_management).pack(pady=5)

    def handle_add_supplier(self, pid, name):
        try:
            pid = int(pid)
            success, message = self.supplier_manager.add_supplier(pid, name)
            messagebox.showinfo("Add Supplier", message)
            if success:
                self.supplier_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid product ID")

    def edit_supplier_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Edit Supplier", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Supplier ID:").pack()
        sid_entry = tk.Entry(self.root)
        sid_entry.pack()
        tk.Label(self.root, text="New Product ID:").pack()
        pid_entry = tk.Entry(self.root)
        pid_entry.pack()
        tk.Label(self.root, text="New Supplier Name:").pack()
        name_entry = tk.Entry(self.root)
        name_entry.pack()
        tk.Button(self.root, text="Update", command=lambda: self.handle_edit_supplier(sid_entry.get(), pid_entry.get(), name_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.supplier_management).pack(pady=5)

    def handle_edit_supplier(self, sid, pid, name):
        try:
            sid = int(sid)
            pid = int(pid)
            success, message = self.supplier_manager.edit_supplier(sid, pid, name)
            messagebox.showinfo("Edit Supplier", message)
            if success:
                self.supplier_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid input")

    def delete_supplier_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Delete Supplier", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Supplier ID:").pack()
        sid_entry = tk.Entry(self.root)
        sid_entry.pack()
        tk.Button(self.root, text="Delete", command=lambda: self.handle_delete_supplier(sid_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.supplier_management).pack(pady=5)

    def handle_delete_supplier(self, sid):
        try:
            sid = int(sid)
            success, message = self.supplier_manager.delete_supplier(sid)
            messagebox.showinfo("Delete Supplier", message)
            if success:
                self.supplier_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid supplier ID")

    def view_all_suppliers(self):
        self.clear_window()
        tk.Label(self.root, text="All Suppliers", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(self.root, columns=("Supplier ID", "Product ID", "Product Name", "Supplier Name"), show="headings")
        tree.heading("Supplier ID", text="Supplier ID")
        tree.heading("Product ID", text="Product ID")
        tree.heading("Product Name", text="Product Name")
        tree.heading("Supplier Name", text="Supplier Name")
        tree.pack(fill="both", expand=True)
        for supplier in self.supplier_manager.get_all_suppliers():
            tree.insert("", "end", values=supplier)
        tk.Button(self.root, text="Back", command=self.supplier_management).pack(pady=5)

    def sales_management(self):
        self.clear_window()
        tk.Label(self.root, text="Sales Management", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Add Sale", command=self.add_sale_ui).pack(pady=5)
        tk.Button(self.root, text="Edit Sale", command=self.edit_sale_ui).pack(pady=5)
        tk.Button(self.root, text="Delete Sale", command=self.delete_sale_ui).pack(pady=5)
        tk.Button(self.root, text="View All Sales", command=self.view_all_sales).pack(pady=5)
        tk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu).pack(pady=5)

    def add_sale_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Add Sale", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Stock ID:").pack()
        sid_entry = tk.Entry(self.root)
        sid_entry.pack()
        tk.Label(self.root, text="Amount Sold:").pack()
        amount_entry = tk.Entry(self.root)
        amount_entry.pack()
        tk.Button(self.root, text="Add", command=lambda: self.handle_add_sale(sid_entry.get(), amount_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.sales_management).pack(pady=5)

    def handle_add_sale(self, sid, amount):
        try:
            sid = int(sid)
            success, message = self.sale_manager.add_sale(sid, amount)
            messagebox.showinfo("Add Sale", message)
            if success:
                self.sales_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid input")

    def edit_sale_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Edit Sale", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Sale ID:").pack()
        sid_entry = tk.Entry(self.root)
        sid_entry.pack()
        tk.Label(self.root, text="New Amount Sold:").pack()
        amount_entry = tk.Entry(self.root)
        amount_entry.pack()
        tk.Button(self.root, text="Update", command=lambda: self.handle_edit_sale(sid_entry.get(), amount_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.sales_management).pack(pady=5)

    def handle_edit_sale(self, sid, amount):
        try:
            sid = int(sid)
            success, message = self.sale_manager.edit_sale(sid, amount)
            messagebox.showinfo("Edit Sale", message)
            if success:
                self.sales_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid input")

    def delete_sale_ui(self):
        self.clear_window()
        tk.Label(self.root, text="Delete Sale", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text="Sale ID:").pack()
        sid_entry = tk.Entry(self.root)
        sid_entry.pack()
        tk.Button(self.root, text="Delete", command=lambda: self.handle_delete_sale(sid_entry.get())).pack(pady=5)
        tk.Button(self.root, text="Back", command=self.sales_management).pack(pady=5)

    def handle_delete_sale(self, sid):
        try:
            sid = int(sid)
            success, message = self.sale_manager.delete_sale(sid)
            messagebox.showinfo("Delete Sale", message)
            if success:
                self.sales_management()
        except ValueError:
            messagebox.showerror("Error", "Invalid sale ID")

    def view_all_sales(self):
        self.clear_window()
        tk.Label(self.root, text="All Sales", font=("Arial", 14)).pack(pady=10)
        tree = ttk.Treeview(self.root, columns=("Sale ID", "Stock ID", "Product Name", "Amount Sold"), show="headings")
        tree.heading("Sale ID", text="Sale ID")
        tree.heading("Stock ID", text="Stock ID")
        tree.heading("Product Name", text="Product Name")
        tree.heading("Amount Sold", text="Amount Sold")
        tree.pack(fill="both", expand=True)
        for sale in self.sale_manager.get_all_sales():
            tree.insert("", "end", values=sale)
        tk.Button(self.root, text="Back", command=self.sales_management).pack(pady=5)

    def generate_reports(self):
        self.clear_window()
        tk.Label(self.root, text="Reports", font=("Arial", 14)).pack(pady=10)
        cursor = self.pm.conn.cursor()

        # Products Report
        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()
        products_df = pd.DataFrame(products, columns=["Product ID", "Product Name", "Price"])
        tk.Label(self.root, text="Products Report", font=("Arial", 12)).pack()
        tree = ttk.Treeview(self.root, columns=("Product ID", "Product Name", "Price"), show="headings")
        tree.heading("Product ID", text="Product ID")
        tree.heading("Product Name", text="Product Name")
        tree.heading("Price", text="Price")
        tree.pack(fill="both", expand=True)
        for product in products:
            tree.insert("", "end", values=product)

        # Stock Report
        cursor.execute("""
        SELECT s.stock_id, p.product_name, s.stock_quantity 
        FROM stocks s 
        JOIN products p ON s.product_id = p.product_id
        """)
        stocks = cursor.fetchall()
        stocks_df = pd.DataFrame(stocks, columns=["Stock ID", "Product Name", "Quantity"])
        tk.Label(self.root, text="Stock Report", font=("Arial", 12)).pack()
        tree = ttk.Treeview(self.root, columns=("Stock ID", "Product Name", "Quantity"), show="headings")
        tree.heading("Stock ID", text="Stock ID")
        tree.heading("Product Name", text="Product Name")
        tree.heading("Quantity", text="Quantity")
        tree.pack(fill="both", expand=True)
        for stock in stocks:
            tree.insert("", "end", values=stock)

        # Supplier Report
        cursor.execute("""
        SELECT sup.supplier_id, p.product_name, sup.supplier_name
        FROM suppliers sup
        JOIN products p ON sup.product_id = p.product_id
        """)
        suppliers = cursor.fetchall()
        suppliers_df = pd.DataFrame(suppliers, columns=["Supplier ID", "Product Name", "Supplier Name"])
        tk.Label(self.root, text="Suppliers Report", font=("Arial", 12)).pack()
        tree = ttk.Treeview(self.root, columns=("Supplier ID", "Product Name", "Supplier Name"), show="headings")
        tree.heading("Supplier ID", text="Supplier ID")
        tree.heading("Product Name", text="Product Name")
        tree.heading("Supplier Name", text="Supplier Name")
        tree.pack(fill="both", expand=True)
        for supplier in suppliers:
            tree.insert("", "end", values=supplier)

        # Sales Report
        cursor.execute("""
        SELECT sa.sale_id, p.product_name, sa.amount_sold
        FROM sales sa
        JOIN stocks st ON sa.stock_id = st.stock_id
        JOIN products p ON st.product_id = p.product_id
        """)
        sales = cursor.fetchall()
        sales_df = pd.DataFrame(sales, columns=["Sale ID", "Product Name", "Amount Sold"])
        tk.Label(self.root, text="Sales Report", font=("Arial", 12)).pack()
        tree = ttk.Treeview(self.root, columns=("Sale ID", "Product Name", "Amount Sold"), show="headings")
        tree.heading("Sale ID", text="Sale ID")
        tree.heading("Product Name", text="Product Name")
        tree.heading("Amount Sold", text="Amount Sold")
        tree.pack(fill="both", expand=True)
        for sale in sales:
            tree.insert("", "end", values=sale)

        # Visualizations
        if not stocks_df.empty:
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(stocks_df["Product Name"], stocks_df["Quantity"], color='skyblue')
            ax.set_title("Stock Quantity per Product")
            ax.set_xlabel("Product")
            ax.set_ylabel("Quantity")
            plt.xticks(rotation=45)
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.root)
            canvas.draw()
            canvas.get_tk_widget().pack()

        if not sales_df.empty:
            sales_summary = sales_df.groupby("Product Name")["Amount Sold"].sum()
            fig, ax = plt.subplots(figsize=(8, 5))
            sales_summary.plot(kind="bar", color='orange', ax=ax)
            ax.set_title("Total Sales per Product")
            ax.set_xlabel("Product")
            ax.set_ylabel("Units Sold")
            plt.xticks(rotation=45)
            plt.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=self.root)
            canvas.draw()
            canvas.get_tk_widget().pack()

        if not products_df.empty:
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.pie(products_df["Price"], labels=products_df["Product Name"], autopct='%1.1f%%')
            ax.set_title("Price Distribution")
            canvas = FigureCanvasTkAgg(fig, master=self.root)
            canvas.draw()
            canvas.get_tk_widget().pack()

        tk.Button(self.root, text="Back to Main Menu", command=self.create_main_menu).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()