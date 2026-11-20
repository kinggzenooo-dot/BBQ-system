"""
Automated End-to-End Verification Test for BBQ House Python Backend & Database.
"""

import sys
from fastapi.testclient import TestClient
from main import app
from database import db

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("🧪 STARTING BBQ HOUSE SYSTEM AUTOMATED TESTS")
    print("=" * 60)

    # 1. Health check
    print("\n[TEST 1] Checking API health endpoint...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health = res.json()
    print("✅ Health check OK:", health)

    # 2. Categories
    print("\n[TEST 2] Checking categories list...")
    res = client.get("/api/categories")
    assert res.status_code == 200
    cats = res.json()
    assert len(cats) >= 5, "Expected at least 5 categories"
    print(f"✅ Fetched {len(cats)} categories successfully.")

    # 3. Products
    print("\n[TEST 3] Checking products list...")
    res = client.get("/api/products")
    assert res.status_code == 200
    prods = res.json()
    assert len(prods) >= 10, "Expected at least 10 products"
    first_prod = prods[0]
    print(f"✅ Fetched {len(prods)} products. Sample item: '{first_prod['name']}' - ₱{first_prod['price']}")

    # 4. User Registration & Authentication
    print("\n[TEST 4] Testing User Authentication & Registration...")
    test_email = "testrunner@bbqhouse.com"
    # Ensure fresh test user
    try:
        reg_res = client.post("/api/auth/register", json={
            "name": "Automated Tester",
            "email": test_email,
            "password": "testpassword123",
            "role": "customer",
            "phone": "0911-222-3333",
            "address": "Tagbilaran City, Bohol"
        })
        if reg_res.status_code == 200:
            print("✅ User registered successfully.")
    except Exception:
        pass

    # Login
    login_res = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "testpassword123"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    user = login_res.json()["user"]
    print(f"✅ Login successful for {user['name']} ({user['email']})")

    # 5. Place an Order
    print("\n[TEST 5] Testing Order Placement...")
    order_payload = {
        "user_id": user["id"],
        "customer_name": user["name"],
        "customer_email": user["email"],
        "customer_phone": "0911-222-3333",
        "delivery_address": "Poblacion, Tagbilaran, Bohol",
        "order_notes": "Automated test order with extra sauce",
        "total_amount": 184.00,
        "payment_method": "gcash",
        "items": [
            {
                "product_id": first_prod["id"],
                "product_name": first_prod["name"],
                "quantity": 2,
                "price": first_prod["price"],
                "subtotal": first_prod["price"] * 2
            }
        ]
    }
    order_res = client.post("/api/orders", json=order_payload)
    assert order_res.status_code == 200, f"Order placement failed: {order_res.text}"
    order = order_res.json()
    order_id = order["id"]
    print(f"✅ Order #{order_id} created successfully with status '{order['order_status']}'.")

    # 6. Admin Update Order Status
    print(f"\n[TEST 6] Testing Admin Order Status Update on Order #{order_id}...")
    status_res = client.patch(f"/api/orders/{order_id}/status", json={
        "order_status": "preparing",
        "payment_status": "paid"
    })
    assert status_res.status_code == 200
    updated_order = status_res.json()
    assert updated_order["order_status"] == "preparing"
    assert updated_order["payment_status"] == "paid"
    print(f"✅ Order #{order_id} updated to 'preparing' and payment 'paid'.")

    # 7. Dashboard Stats
    print("\n[TEST 7] Testing Dashboard KPI Stats...")
    stats_res = client.get("/api/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_orders"] >= 1
    assert stats["total_revenue"] > 0
    print("✅ Stats verified:", stats)

    # 8. Single-Link Frontend Page Loading
    print("\n[TEST 8] Testing Frontend Single-Link Delivery (index.html)...")
    page_res = client.get("/")
    assert page_res.status_code == 200
    assert "BBQ HOUSE" in page_res.text
    assert "Our Full BBQ Menu" in page_res.text
    print("✅ Single-link frontend (index.html) successfully delivered at '/' (HTTP 200).")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! BACKEND AND DATABASE ARE 100% OPERATIONAL!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
