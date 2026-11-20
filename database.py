"""
BBQ House Database Manager
Unified Data Layer supporting Supabase Cloud Database with automatic SQLite local fallback/sync.
"""

import os
import sqlite3
import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Handle spaced or underscored env variables
SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE URL") or ""
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE ANON KEY") or ""

# Try importing supabase-py
supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"[Supabase Init Warning] {e}")

DB_FILE = Path(__file__).parent / "bbq_store.db"


def hash_password(password: str) -> str:
    """Hash password using bcrypt or fallback securely."""
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    except Exception:
        import hashlib
        return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        import bcrypt
        if hashed_password.startswith("$2b$") or hashed_password.startswith("$2a$"):
            return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        pass

    import hashlib
    if hashlib.sha256(plain_password.encode("utf-8")).hexdigest() == hashed_password:
        return True
    
    # Fallback comparison for plain/dev seeds
    return plain_password == hashed_password


class DatabaseManager:
    def __init__(self):
        self.use_supabase = False
        self.init_sqlite()
        self.check_supabase_tables()

    def check_supabase_tables(self):
        """Check if Supabase has required tables active."""
        if not supabase_client:
            print("[DB] Supabase client not configured. Using local database.")
            self.use_supabase = False
            return

        try:
            res = supabase_client.table("categories").select("id").limit(1).execute()
            if res is not None:
                self.use_supabase = True
                print("[DB] Connected to Supabase Cloud Database successfully!")
                self.ensure_seed_users_valid()
                return
        except Exception as e:
            err_msg = str(e)
            print(f"[DB] Supabase tables not yet created ({err_msg}). Operating on local SQLite store.")
            print("[DB] TIP: Run 'supabase_schema.sql' in your Supabase Dashboard SQL Editor to switch to cloud mode.")
            self.use_supabase = False

    def ensure_seed_users_valid(self):
        """Ensure demo accounts (admin and customer) always have working credentials."""
        try:
            admin_user = self.get_user_by_email("admin@bbqhouse.com")
            if admin_user:
                if not verify_password("admin123", admin_user.get("password", "")):
                    self.update_user(admin_user["id"], {"password": "admin123"})
                    print("[DB] Verified & refreshed admin@bbqhouse.com password.")

            cust_user = self.get_user_by_email("customer@bbqhouse.com")
            if cust_user:
                if not verify_password("customer123", cust_user.get("password", "")):
                    self.update_user(cust_user["id"], {"password": "customer123"})
                    print("[DB] Verified & refreshed customer@bbqhouse.com password.")
        except Exception as e:
            pass

    def get_sqlite_conn(self):
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

    def init_sqlite(self):
        """Initialize SQLite database with identical schema and rich initial BBQ products."""
        conn = self.get_sqlite_conn()
        cursor = conn.cursor()

        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 50,
            image TEXT DEFAULT 'images/products/pork-bbq.jpg',
            status TEXT DEFAULT 'available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'customer',
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            delivery_address TEXT NOT NULL,
            order_notes TEXT,
            total_amount REAL NOT NULL,
            order_status TEXT DEFAULT 'pending',
            payment_method TEXT DEFAULT 'cash_on_delivery',
            payment_status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );

        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            product_id INTEGER,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders (id)
        );
        """)

        # Check if categories already seeded
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            categories_data = [
                ("BBQ Meals", "Hearty and satisfying grilled BBQ combo plates served with garlic rice and atchara."),
                ("BBQ Skewers", "Classic street-style skewered meats grilled with savory-sweet soy and calamansi glaze."),
                ("Chicken BBQ", "Tender, juicy chicken cuts basted with signature spicy-sweet BBQ marinade."),
                ("Pork BBQ", "Authentic tender pork cuts grilled over coconut charcoal to smoky perfection."),
                ("Drinks & Sides", "Ice-cold beverages, extra sauces, garlic rice, and homemade sides.")
            ]
            cursor.executemany("INSERT INTO categories (name, description) VALUES (?, ?)", categories_data)

            products_data = [
                (2, "Classic Pork BBQ Skewer", "2 juicy skewers of marinated pork slices grilled over natural charcoal with sweet-savory glaze.", 35.00, 100, "images/products/pork-bbq.jpg", "available"),
                (3, "Grilled Chicken Inasal Quarter", "Leg and thigh quarter marinated in lemongrass, ginger, vinegar, and annatto oil, grilled fresh.", 135.00, 45, "images/products/chicken-bbq.jpg", "available"),
                (1, "Signature BBQ Rice Meal", "2 Pork BBQ skewers served with unlimited garlic rice, sunny-side egg, and savory BBQ dipping sauce.", 99.00, 60, "images/products/bbq-meal.jpg", "available"),
                (4, "Charcoal Grilled Pork Liempo", "Thick cut succulent pork belly marinated in special spices and grilled to smoky crisp perfection.", 165.00, 35, "images/products/pork-bbq.jpg", "available"),
                (3, "Chicken BBQ Skewer Platter", "5 pieces of tender boneless chicken BBQ skewers basted with our secret house sauce.", 180.00, 30, "images/products/chicken-bbq.jpg", "available"),
                (1, "Grilled Liempo Meal Deal", "Generous slice of grilled liempo served with steamed garlic rice, soup, and atchara.", 175.00, 40, "images/products/bbq-meal.jpg", "available"),
                (2, "Isaw Manok (Chicken Skewers)", "Popular street-food favorite, thoroughly cleaned and barbecued crispy with spiced vinegar.", 25.00, 120, "images/products/chicken-bbq.jpg", "available"),
                (5, "Extra Garlic Rice", "Hot freshly cooked cup of steamed garlic butter rice.", 25.00, 150, "images/products/bbq-meal.jpg", "available"),
                (5, "Ice-Cold Coca-Cola (330ml)", "Refreshing chilled carbonated cola in can.", 35.00, 80, "images/products/coke.jpg", "available"),
                (5, "Purified Mineral Water (500ml)", "Pure drinking water in sealed bottle.", 20.00, 100, "images/products/water.jpg", "available")
            ]
            cursor.executemany("""
                INSERT INTO products (category_id, name, description, price, stock, image, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, products_data)

            # Insert default admin and customer
            admin_pwd = hash_password("admin123")
            cust_pwd = hash_password("customer123")
            users_data = [
                ("BBQ Store Admin", "admin@bbqhouse.com", admin_pwd, "admin", "0912-345-6789", "Main Branch, BBQ House, Bohol"),
                ("Juan Dela Cruz", "customer@bbqhouse.com", cust_pwd, "customer", "0998-765-4321", "123 Rizal Street, Tagbilaran City, Bohol")
            ]
            cursor.executemany("""
                INSERT INTO users (name, email, password, role, phone, address)
                VALUES (?, ?, ?, ?, ?, ?)
            """, users_data)

            # Insert sample order
            cursor.execute("""
                INSERT INTO orders (user_id, customer_name, customer_email, customer_phone, delivery_address, order_notes, total_amount, order_status, payment_method, payment_status)
                VALUES (2, 'Juan Dela Cruz', 'customer@bbqhouse.com', '0998-765-4321', '123 Rizal Street, Tagbilaran City, Bohol', 'Please include extra spicy BBQ sauce', 184.00, 'preparing', 'cash_on_delivery', 'pending')
            """)
            sample_order_id = cursor.lastrowid

            cursor.executemany("""
                INSERT INTO order_items (order_id, product_id, product_name, quantity, price, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, [
                (sample_order_id, 3, "Signature BBQ Rice Meal", 1, 99.00, 99.00),
                (sample_order_id, 1, "Classic Pork BBQ Skewer", 1, 35.00, 35.00),
                (sample_order_id, 9, "Ice-Cold Coca-Cola (330ml)", 1, 35.00, 35.00)
            ])

        conn.commit()
        conn.close()

    # -------------------------------------------------------------
    # CATEGORIES
    # -------------------------------------------------------------
    def get_categories(self):
        if self.use_supabase:
            try:
                res = supabase_client.table("categories").select("*").order("id").execute()
                return res.data or []
            except Exception as e:
                print(f"[Supabase Error categories] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY id ASC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def create_category(self, name: str, description: str = ""):
        if self.use_supabase:
            try:
                res = supabase_client.table("categories").insert({"name": name, "description": description}).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"[Supabase Error create_category] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
        cat_id = cursor.lastrowid
        conn.commit()
        cursor.execute("SELECT * FROM categories WHERE id = ?", (cat_id,))
        row = dict(cursor.fetchone())
        conn.close()
        return row

    def delete_category(self, category_id: int):
        if self.use_supabase:
            try:
                supabase_client.table("categories").delete().eq("id", category_id).execute()
                return True
            except Exception as e:
                print(f"[Supabase Error delete_category] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        conn.commit()
        conn.close()
        return True

    # -------------------------------------------------------------
    # PRODUCTS
    # -------------------------------------------------------------
    def get_products(self, category_id=None, search=None):
        if self.use_supabase:
            try:
                query = supabase_client.table("products").select("*, categories(name)")
                if category_id:
                    query = query.eq("category_id", int(category_id))
                res = query.order("id").execute()
                products = []
                for p in res.data or []:
                    cat_info = p.get("categories")
                    p["category_name"] = cat_info["name"] if cat_info and "name" in cat_info else "Uncategorized"
                    if search and search.lower() not in p["name"].lower() and search.lower() not in (p.get("description") or "").lower():
                        continue
                    products.append(p)
                return products
            except Exception as e:
                print(f"[Supabase Error get_products] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        query = """
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE 1=1
        """
        params = []
        if category_id:
            query += " AND p.category_id = ?"
            params.append(category_id)
        if search:
            query += " AND (p.name LIKE ? OR p.description LIKE ?)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")

        query += " ORDER BY p.id ASC"
        cursor.execute(query, params)
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    def get_product(self, product_id: int):
        if self.use_supabase:
            try:
                res = supabase_client.table("products").select("*, categories(name)").eq("id", product_id).execute()
                if res.data:
                    p = res.data[0]
                    cat_info = p.get("categories")
                    p["category_name"] = cat_info["name"] if cat_info and "name" in cat_info else "Uncategorized"
                    return p
            except Exception as e:
                print(f"[Supabase Error get_product] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, c.name as category_name
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = ?
        """, (product_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def create_product(self, data: dict):
        if self.use_supabase:
            try:
                res = supabase_client.table("products").insert({
                    "name": data.get("name"),
                    "category_id": data.get("category_id"),
                    "description": data.get("description", ""),
                    "price": float(data.get("price", 0)),
                    "stock": int(data.get("stock", 0)),
                    "image": data.get("image", "images/products/pork-bbq.jpg"),
                    "status": data.get("status", "available")
                }).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"[Supabase Error create_product] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, category_id, description, price, stock, image, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("name"),
            data.get("category_id"),
            data.get("description", ""),
            float(data.get("price", 0)),
            int(data.get("stock", 0)),
            data.get("image", "images/products/pork-bbq.jpg"),
            data.get("status", "available")
        ))
        prod_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.get_product(prod_id)

    def update_product(self, product_id: int, data: dict):
        if self.use_supabase:
            try:
                payload = {}
                for k in ["name", "category_id", "description", "price", "stock", "image", "status"]:
                    if k in data:
                        payload[k] = data[k]
                res = supabase_client.table("products").update(payload).eq("id", product_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"[Supabase Error update_product] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        fields = []
        params = []
        for k in ["name", "category_id", "description", "price", "stock", "image", "status"]:
            if k in data:
                fields.append(f"{k} = ?")
                params.append(data[k])
        if not fields:
            conn.close()
            return self.get_product(product_id)

        params.append(product_id)
        cursor.execute(f"UPDATE products SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
        conn.close()
        return self.get_product(product_id)

    def delete_product(self, product_id: int):
        if self.use_supabase:
            try:
                supabase_client.table("products").delete().eq("id", product_id).execute()
                return True
            except Exception as e:
                print(f"[Supabase Error delete_product] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        return True

    # -------------------------------------------------------------
    # USERS & AUTH
    # -------------------------------------------------------------
    def get_user_by_email(self, email: str):
        email_clean = email.strip().lower()
        if self.use_supabase:
            try:
                res = supabase_client.table("users").select("*").eq("email", email_clean).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"[Supabase Error get_user_by_email] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email_clean,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_user_by_id(self, user_id: int):
        if self.use_supabase:
            try:
                res = supabase_client.table("users").select("id, name, email, role, phone, address, created_at").eq("id", user_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"[Supabase Error get_user_by_id] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, role, phone, address, created_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def register_user(self, name: str, email: str, password: str, role: str = "customer", phone: str = "", address: str = ""):
        email_clean = email.strip().lower()
        if self.get_user_by_email(email_clean):
            raise ValueError("An account with this email already exists.")

        pwd_hash = hash_password(password)

        if self.use_supabase:
            try:
                res = supabase_client.table("users").insert({
                    "name": name.strip(),
                    "email": email_clean,
                    "password": pwd_hash,
                    "role": role,
                    "phone": phone,
                    "address": address
                }).execute()
                if res.data:
                    user = res.data[0]
                    user.pop("password", None)
                    return user
            except Exception as e:
                print(f"[Supabase Error register_user] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (name, email, password, role, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name.strip(), email_clean, pwd_hash, role, phone, address))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return self.get_user_by_id(user_id)

    def authenticate_user(self, email: str, password: str):
        user = self.get_user_by_email(email)
        if not user:
            return None
        if verify_password(password, user["password"]):
            user_safe = dict(user)
            user_safe.pop("password", None)
            return user_safe
        return None

    def update_user(self, user_id: int, data: dict):
        payload = {}
        for k in ["name", "email", "phone", "address"]:
            if k in data and data[k] is not None:
                payload[k] = data[k]
        if "password" in data and data["password"]:
            payload["password"] = hash_password(data["password"])

        if self.use_supabase:
            try:
                res = supabase_client.table("users").update(payload).eq("id", user_id).execute()
                if res.data:
                    u = res.data[0]
                    u.pop("password", None)
                    return u
            except Exception as e:
                print(f"[Supabase Error update_user] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        fields = []
        params = []
        for k, v in payload.items():
            fields.append(f"{k} = ?")
            params.append(v)
        if not fields:
            conn.close()
            return self.get_user_by_id(user_id)

        params.append(user_id)
        cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = ?", params)
        conn.commit()
        conn.close()
        return self.get_user_by_id(user_id)

    def get_customers(self):
        if self.use_supabase:
            try:
                res = supabase_client.table("users").select("id, name, email, role, phone, address, created_at").order("id", desc=True).execute()
                return res.data or []
            except Exception as e:
                print(f"[Supabase Error get_customers] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email, role, phone, address, created_at FROM users ORDER BY id DESC")
        rows = [dict(r) for r in cursor.fetchall()]
        conn.close()
        return rows

    # -------------------------------------------------------------
    # ORDERS
    # -------------------------------------------------------------
    def create_order(self, order_data: dict, items: list):
        if not items:
            raise ValueError("Order must contain at least one item.")

        total_amount = float(order_data.get("total_amount", 0))
        user_id = order_data.get("user_id")

        if self.use_supabase:
            try:
                # Validate user_id exists in Supabase to prevent foreign key errors
                valid_user_id = None
                if user_id:
                    try:
                        u_chk = supabase_client.table("users").select("id").eq("id", int(user_id)).execute()
                        if u_chk.data:
                            valid_user_id = int(user_id)
                    except Exception:
                        valid_user_id = None

                ord_res = supabase_client.table("orders").insert({
                    "user_id": valid_user_id,
                    "customer_name": order_data.get("customer_name"),
                    "customer_email": order_data.get("customer_email"),
                    "customer_phone": order_data.get("customer_phone"),
                    "delivery_address": order_data.get("delivery_address"),
                    "order_notes": order_data.get("order_notes", ""),
                    "total_amount": total_amount,
                    "order_status": "pending",
                    "payment_method": order_data.get("payment_method", "cash_on_delivery"),
                    "payment_status": "pending"
                }).execute()

                if ord_res.data:
                    order_id = ord_res.data[0]["id"]
                    order_items_payload = []
                    for it in items:
                        order_items_payload.append({
                            "order_id": order_id,
                            "product_id": it.get("product_id"),
                            "product_name": it.get("product_name"),
                            "quantity": int(it.get("quantity", 1)),
                            "price": float(it.get("price", 0)),
                            "subtotal": float(it.get("subtotal", 0))
                        })
                    supabase_client.table("order_items").insert(order_items_payload).execute()
                    return self.get_order(order_id)
            except Exception as e:
                print(f"[Supabase Error create_order] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (user_id, customer_name, customer_email, customer_phone, delivery_address, order_notes, total_amount, order_status, payment_method, payment_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_data.get("user_id"),
            order_data.get("customer_name"),
            order_data.get("customer_email"),
            order_data.get("customer_phone"),
            order_data.get("delivery_address"),
            order_data.get("order_notes", ""),
            total_amount,
            "pending",
            order_data.get("payment_method", "cash_on_delivery"),
            "pending"
        ))
        order_id = cursor.lastrowid

        for it in items:
            cursor.execute("""
                INSERT INTO order_items (order_id, product_id, product_name, quantity, price, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                it.get("product_id"),
                it.get("product_name"),
                int(it.get("quantity", 1)),
                float(it.get("price", 0)),
                float(it.get("subtotal", 0))
            ))

            # Reduce product stock
            if it.get("product_id"):
                cursor.execute("""
                    UPDATE products SET stock = MAX(0, stock - ?) WHERE id = ?
                """, (int(it.get("quantity", 1)), it.get("product_id")))

        conn.commit()
        conn.close()
        return self.get_order(order_id)

    def get_orders(self, user_id=None, status=None):
        if self.use_supabase:
            try:
                query = supabase_client.table("orders").select("*, order_items(*)")
                if user_id:
                    query = query.eq("user_id", int(user_id))
                if status and status != "all":
                    query = query.eq("order_status", status)
                res = query.order("id", desc=True).execute()
                return res.data or []
            except Exception as e:
                print(f"[Supabase Error get_orders] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        query = "SELECT * FROM orders WHERE 1=1"
        params = []
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if status and status != "all":
            query += " AND order_status = ?"
            params.append(status)
        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        orders = [dict(r) for r in cursor.fetchall()]

        for ord in orders:
            cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (ord["id"],))
            ord["items"] = [dict(i) for i in cursor.fetchall()]

        conn.close()
        return orders

    def get_order(self, order_id: int):
        if self.use_supabase:
            try:
                res = supabase_client.table("orders").select("*, order_items(*)").eq("id", order_id).execute()
                if res.data:
                    return res.data[0]
            except Exception as e:
                print(f"[Supabase Error get_order] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        order = dict(row)
        cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        order["items"] = [dict(i) for i in cursor.fetchall()]
        conn.close()
        return order

    def update_order_status(self, order_id: int, status: str, payment_status: str = None):
        if self.use_supabase:
            try:
                payload = {"order_status": status}
                if payment_status:
                    payload["payment_status"] = payment_status
                res = supabase_client.table("orders").update(payload).eq("id", order_id).execute()
                if res.data:
                    return self.get_order(order_id)
            except Exception as e:
                print(f"[Supabase Error update_order_status] {e}")

        conn = self.get_sqlite_conn()
        cursor = conn.cursor()
        if payment_status:
            cursor.execute("""
                UPDATE orders SET order_status = ?, payment_status = ? WHERE id = ?
            """, (status, payment_status, order_id))
        else:
            cursor.execute("""
                UPDATE orders SET order_status = ? WHERE id = ?
            """, (status, order_id))
        conn.commit()
        conn.close()
        return self.get_order(order_id)

    # -------------------------------------------------------------
    # STATS & DASHBOARD
    # -------------------------------------------------------------
    def get_dashboard_stats(self):
        conn = self.get_sqlite_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE order_status != 'cancelled'")
        total_revenue = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM orders WHERE order_status IN ('pending', 'confirmed', 'preparing', 'ready', 'out_for_delivery')")
        active_orders = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
        total_customers = cursor.fetchone()[0]

        cursor.execute("""
            SELECT order_status, COUNT(*) as count 
            FROM orders 
            GROUP BY order_status
        """)
        status_counts = {r["order_status"]: r["count"] for r in cursor.fetchall()}

        conn.close()

        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "active_orders": active_orders,
            "total_products": total_products,
            "total_customers": total_customers,
            "status_counts": status_counts,
            "backend_db": "Supabase Cloud" if self.use_supabase else "Local SQLite (Ready to sync with Supabase)"
        }


# Singleton database instance
db = DatabaseManager()
