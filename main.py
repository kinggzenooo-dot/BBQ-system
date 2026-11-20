"""
BBQ House - FastAPI Backend
Complete Python Backend serving REST APIs and Unified Single-Link Frontend.
"""

import os
from typing import Optional, List, Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, EmailStr

from database import db, hash_password, verify_password

app = FastAPI(
    title="BBQ House Online Store API",
    description="Python backend for BBQ House online store with Supabase integration",
    version="2.0.0"
)

# Enable CORS for local and external requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent

# Mount Static Folders
if (BASE_DIR / "css").exists():
    app.mount("/css", StaticFiles(directory=str(BASE_DIR / "css")), name="css")
if (BASE_DIR / "js").exists():
    app.mount("/js", StaticFiles(directory=str(BASE_DIR / "js")), name="js")
if (BASE_DIR / "images").exists():
    app.mount("/images", StaticFiles(directory=str(BASE_DIR / "images")), name="images")


# =====================================================================
# PYDANTIC SCHEMAS
# =====================================================================

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: Optional[str] = "customer"
    phone: Optional[str] = ""
    address: Optional[str] = ""

class LoginRequest(BaseModel):
    email: str
    password: str

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class CategoryCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""

class ProductCreateRequest(BaseModel):
    name: str
    category_id: Optional[int] = None
    description: Optional[str] = ""
    price: float
    stock: Optional[int] = 50
    image: Optional[str] = "images/products/pork-bbq.jpg"
    status: Optional[str] = "available"

class ProductUpdateRequest(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    image: Optional[str] = None
    status: Optional[str] = None

class OrderItemModel(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    quantity: int
    price: float
    subtotal: float

class OrderCreateRequest(BaseModel):
    user_id: Optional[int] = None
    customer_name: str
    customer_email: str
    customer_phone: str
    delivery_address: str
    order_notes: Optional[str] = ""
    total_amount: float
    payment_method: Optional[str] = "cash_on_delivery"
    items: List[OrderItemModel]

class OrderStatusUpdateRequest(BaseModel):
    order_status: str
    payment_status: Optional[str] = None


# =====================================================================
# REST API ROUTES
# =====================================================================

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "BBQ House Online Store Backend",
        "database": "Supabase Cloud" if db.use_supabase else "Local SQLite (Ready to sync with Supabase)",
        "supabase_configured": bool(db.use_supabase or (os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")))
    }

@app.get("/api/stats")
def get_stats():
    return db.get_dashboard_stats()

# Categories
@app.get("/api/categories")
def list_categories():
    return db.get_categories()

@app.post("/api/categories")
def create_category(cat: CategoryCreateRequest):
    return db.create_category(cat.name, cat.description)

@app.delete("/api/categories/{category_id}")
def delete_category(category_id: int):
    db.delete_category(category_id)
    return {"message": "Category deleted successfully"}

# Products
@app.get("/api/products")
def list_products(category_id: Optional[int] = None, search: Optional[str] = None):
    return db.get_products(category_id=category_id, search=search)

@app.get("/api/products/{product_id}")
def get_product(product_id: int):
    prod = db.get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

@app.post("/api/products")
def create_product(prod: ProductCreateRequest):
    return db.create_product(prod.dict())

@app.put("/api/products/{product_id}")
def update_product(product_id: int, prod: ProductUpdateRequest):
    data = {k: v for k, v in prod.dict().items() if v is not None}
    updated = db.update_product(product_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int):
    db.delete_product(product_id)
    return {"message": "Product deleted successfully"}

# Orders
@app.get("/api/orders")
def list_orders(user_id: Optional[int] = None, status: Optional[str] = None):
    return db.get_orders(user_id=user_id, status=status)

@app.get("/api/orders/{order_id}")
def get_order(order_id: int):
    order = db.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.post("/api/orders")
def create_order(req: OrderCreateRequest):
    try:
        order_dict = req.dict()
        items_dict = order_dict.pop("items")
        order = db.create_order(order_dict, items_dict)
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/api/orders/{order_id}/status")
def update_order_status(order_id: int, req: OrderStatusUpdateRequest):
    order = db.update_order_status(order_id, req.order_status, req.payment_status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

# Authentication & Users
@app.post("/api/auth/register")
def register(req: RegisterRequest):
    try:
        user = db.register_user(
            name=req.name,
            email=req.email,
            password=req.password,
            role=req.role or "customer",
            phone=req.phone or "",
            address=req.address or ""
        )
        return {"message": "Registration successful", "user": user}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/auth/login")
def login(req: LoginRequest):
    user = db.authenticate_user(req.email, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"message": "Login successful", "user": user}

@app.put("/api/auth/users/{user_id}")
def update_user_profile(user_id: int, req: UserUpdateRequest):
    data = {k: v for k, v in req.dict().items() if v is not None}
    updated = db.update_user(user_id, data)
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "Profile updated successfully", "user": updated}

@app.get("/api/customers")
def list_customers():
    return db.get_customers()


# =====================================================================
# UNIFIED SINGLE-LINK FRONTEND ROUTE
# =====================================================================

@app.get("/")
def serve_index():
    index_file = BASE_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "BBQ House API is running. index.html not found."}


# Catch-all for SPA routes
@app.get("/{full_path:path}")
def catch_all(full_path: str):
    # If file exists in base dir, serve it
    requested_file = BASE_DIR / full_path
    if requested_file.is_file():
        return FileResponse(requested_file)
    
    # Otherwise fallback to single-link index.html
    index_file = BASE_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Not Found")
