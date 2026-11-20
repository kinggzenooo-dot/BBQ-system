# 🔥 BBQ House - Online Store & Real-Time Ordering System

A full-stack, single-link online BBQ ordering system with a **Python FastAPI backend** and **Supabase PostgreSQL database** integration.

---

## 🌟 Key Features

- **Single-Link Web Experience**: The customer storefront, live menu, cart, checkout, live order tracking, and administrative dashboard all operate seamlessly from **a single unified link (`http://localhost:8000`)**.
- **Real-Time Data Synchronization**:
  - Products added or edited by the Admin immediately sync to the customer menu.
  - Orders placed by customers instantly appear in the Admin dashboard.
  - Order status updates (Pending 🕒 → Confirmed ✅ → Preparing 🔥 → Ready 📦 → Out for Delivery 🚴 → Delivered 🎉) update live in the customer order tracker.
- **Python Backend**: Migrated from legacy PHP to a modern, lightning-fast **FastAPI** backend with automated OpenAPI interactive documentation (`/docs`).
- **Supabase Cloud Database Ready**: Includes full PostgreSQL schema (`supabase_schema.sql`), automated table detection, and resilient fallback/sync capabilities.
- **Cart & Checkout**: Interactive slide-out cart drawer with item counter badge, stock validation, and multiple payment methods (Cash on Delivery, GCash, Maya).
- **Role-Based Authentication**: Secure customer and admin accounts with hashed passwords and quick 1-click demo login buttons.

---

## 📂 Project Structure

```text
BBQ-ONLINE-STORE/
├── css/
│   ├── style.css             # Main styling, responsive grids & UI components
├── js/
│   ├── app.js                # Single-link SPA controller & real-time sync
├── images/
│   ├── banner.jpg            # Hero banner image
│   └── products/             # BBQ product photography & visuals
├── database/
│   ├── schema.sql            # PostgreSQL schema script
│   └── bbq_store.sql         # Legacy MySQL dump (reference)
├── main.py                   # FastAPI application & REST API routes
├── database.py               # Database manager (Supabase + local SQLite fallback)
├── run.py                    # Server launch entry point
├── test_system.py            # Automated end-to-end test suite
├── supabase_schema.sql       # Copy-paste ready SQL for Supabase SQL Editor
├── requirements.txt          # Python dependencies
├── .env.example              # Environment variables template
├── .env                      # Active environment configuration
└── index.html                # Unified single-link frontend application
```

---

## 🗄️ Supabase Database Setup

Your Supabase credentials are configured in `.env`:

```env
SUPABASE_URL=https://jjqlesittpjaweoeiixy.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
PORT=8000
HOST=0.0.0.0
```

### To apply the database schema in Supabase:
1. Open your [Supabase Dashboard](https://supabase.com/dashboard).
2. Go to the **SQL Editor** from the left sidebar.
3. Open or copy the contents of `supabase_schema.sql`.
4. Click **Run**.
5. All 5 tables (`categories`, `products`, `users`, `orders`, `order_items`), foreign keys, Row Level Security (RLS) policies, and authentic Pinoy BBQ seed items will be created instantly.

> **Note**: If Supabase tables are still being set up, the backend runs gracefully with its local database and connects to Supabase as soon as the tables are created.

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Automated System Tests
Verify that the database, APIs, authentication, and order workflows are working:
```bash
python test_system.py
```

### 3. Start the Server
Launch the application:
```bash
python run.py
```

Open your browser to:
👉 **`http://localhost:8000`**

Interactive API Swagger documentation is available at:
👉 **`http://localhost:8000/docs`**

---

## 🔑 Demo Accounts

Use these pre-seeded accounts for testing:

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@bbqhouse.com` | `admin123` |
| **Customer** | `customer@bbqhouse.com` | `customer123` |

*(Tip: In the Login modal, you can also click the quick buttons **👤 Customer** or **👑 Admin** to auto-fill the form!)*

---

## 📡 API Endpoints Summary

- `GET /api/health` - System health and database connection status
- `GET /api/stats` - Dashboard metrics (revenue, orders, active grilling, customer counts)
- `GET /api/categories` - List BBQ categories
- `GET /api/products` - List menu items (supports `?category_id=` and `?search=`)
- `POST /api/products` - Admin: Create new product
- `PUT /api/products/{id}` - Admin: Update product details and inventory
- `DELETE /api/products/{id}` - Admin: Delete product
- `GET /api/orders` - List customer orders
- `POST /api/orders` - Place a new order with items
- `GET /api/orders/{id}` - Fetch details & status for real-time tracking
- `PATCH /api/orders/{id}/status` - Admin: Update order status & payment
- `POST /api/auth/register` - Create customer or admin account
- `POST /api/auth/login` - Authenticate user
- `GET /api/customers` - Admin: List customer accounts


---

## 🚀 Deploying to Render (render.com)

This repository is pre-configured with `render.yaml` and `Procfile` for 1-click deployment on Render.

### Step-by-Step Render Deployment:

1. **Sign in to Render**: Go to [render.com](https://render.com) and log in with your GitHub account.
2. **Create New Web Service**:
   - In the Render dashboard, click **New +** $\rightarrow$ **Web Service**.
   - Connect your repository: `https://github.com/kinggzenooo-dot/BBQ-system.git`.
3. **Configure Service**:
   - **Name**: `bbq-online-store` (or any name you prefer)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: `Free`
4. **Environment Variables**:
   Under **Environment Variables**, add:
   - `SUPABASE_URL`: `https://jjqlesittpjaweoeiixy.supabase.co`
   - `SUPABASE_KEY`: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (your anon key from `.env`)
   - `SUPABASE_ANON_KEY`: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - `SECRET_KEY`: `bbq-house-secret-key-2026`
5. **Click "Deploy Web Service"**:
   Render will automatically build and launch your single-link BBQ store live on the web at a public `.onrender.com` URL!
