"""
Automated End-to-End Verification Test for BBQ House Python Backend & Database.
"""

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

    # 3. Products Listing & PUT Update Persistence
    print("\n[TEST 3] Testing Product Catalog & PUT Update Persistence...")
    res = client.get("/api/products")
    assert res.status_code == 200
    prods = res.json()
    assert len(prods) >= 10, "Expected at least 10 products"
    first_prod = prods[0]
    prod_id = first_prod["id"]
    print(f"✅ Fetched {len(prods)} products. Sample item: '{first_prod['name']}' - ₱{first_prod['price']}")

    # Test PUT product (Update price, stock, and description)
    print(f"   Testing PUT /api/products/{prod_id}...")
    new_price = float(first_prod["price"]) + 5.0
    new_stock = int(first_prod["stock"]) + 10
    put_res = client.put(f"/api/products/{prod_id}", json={
        "name": first_prod["name"],
        "price": new_price,
        "stock": new_stock,
        "description": "Updated freshly grilled BBQ specialty with secret island marinade."
    })
    assert put_res.status_code == 200, f"Product PUT failed: {put_res.text}"
    updated_prod = put_res.json()
    assert updated_prod["price"] == new_price
    assert updated_prod["stock"] == new_stock

    # Verify directly from DB through a fresh GET call
    verify_get = client.get(f"/api/products/{prod_id}").json()
    assert verify_get["price"] == new_price
    print(f"✅ Product PUT verified in database! Saved price: ₱{verify_get['price']}, stock: {verify_get['stock']}")

    # 4. User Registration, Authentication & Credential Saving
    print("\n[TEST 4] Testing User Authentication & Credential Persistence...")
    test_email = "testrunner@bbqhouse.com"
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
            print("✅ User registered and saved to database.")
    except Exception:
        pass

    # Login to authenticate credentials
    login_res = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "testpassword123"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    user = login_res.json()["user"]
    print(f"✅ Credentials authenticated from database for {user['name']} ({user['email']})")

    # Update User Credential / Profile (PUT /api/auth/users/{id})
    user_id = user["id"]
    update_user_res = client.put(f"/api/auth/users/{user_id}", json={
        "name": "Automated Tester Verified",
        "phone": "0999-111-2222",
        "address": "New Branch Address, Bohol"
    })
    assert update_user_res.status_code == 200
    updated_user = update_user_res.json()["user"]
    assert updated_user["name"] == "Automated Tester Verified"
    print(f"✅ Updated credentials saved in database: Name='{updated_user['name']}', Phone='{updated_user['phone']}'")

    # 5. Place an Order
    print("\n[TEST 5] Testing Order Placement...")
    order_payload = {
        "user_id": user["id"],
        "customer_name": updated_user["name"],
        "customer_email": user["email"],
        "customer_phone": updated_user["phone"],
        "delivery_address": updated_user["address"],
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
    print("🎉 ALL TESTS PASSED! BACKEND, DATABASE & CREDENTIALS ARE 100% OPERATIONAL!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
