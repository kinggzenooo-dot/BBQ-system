-- ====================================================================
-- BBQ HOUSE - SUPABASE POSTGRESQL SCHEMA & SEED DATA
-- Project: BBQ Online Store
-- ====================================================================

-- 1. EXTENSIONS
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. DROP EXISTING TABLES (IF RE-RUNNING SCHEMA)
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- 3. CATEGORIES TABLE
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. PRODUCTS TABLE
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    category_id INT REFERENCES categories(id) ON UPDATE CASCADE ON DELETE SET NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    stock INT NOT NULL DEFAULT 50 CHECK (stock >= 0),
    image VARCHAR(255) DEFAULT 'images/products/pork-bbq.jpg',
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'unavailable')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. USERS TABLE
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
    phone VARCHAR(30),
    address TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. ORDERS TABLE
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(150) NOT NULL,
    customer_phone VARCHAR(30) NOT NULL,
    delivery_address TEXT NOT NULL,
    order_notes TEXT,
    total_amount NUMERIC(10, 2) NOT NULL CHECK (total_amount >= 0),
    order_status VARCHAR(30) DEFAULT 'pending' CHECK (order_status IN ('pending', 'confirmed', 'preparing', 'ready', 'out_for_delivery', 'completed', 'cancelled')),
    payment_method VARCHAR(30) DEFAULT 'cash_on_delivery' CHECK (payment_method IN ('cash_on_delivery', 'gcash', 'maya')),
    payment_status VARCHAR(20) DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'failed')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. ORDER ITEMS TABLE
CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INT REFERENCES products(id) ON DELETE SET NULL,
    product_name VARCHAR(150) NOT NULL,
    quantity INT NOT NULL CHECK (quantity > 0),
    price NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    subtotal NUMERIC(10, 2) NOT NULL CHECK (subtotal >= 0)
);

-- ====================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- Enable Row Level Security and allow anon + authenticated access
-- ====================================================================

ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE products ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE order_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read categories" ON categories FOR SELECT USING (true);
CREATE POLICY "Allow public insert categories" ON categories FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update categories" ON categories FOR UPDATE USING (true);
CREATE POLICY "Allow public delete categories" ON categories FOR DELETE USING (true);

CREATE POLICY "Allow public read products" ON products FOR SELECT USING (true);
CREATE POLICY "Allow public insert products" ON products FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update products" ON products FOR UPDATE USING (true);
CREATE POLICY "Allow public delete products" ON products FOR DELETE USING (true);

CREATE POLICY "Allow public read users" ON users FOR SELECT USING (true);
CREATE POLICY "Allow public insert users" ON users FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update users" ON users FOR UPDATE USING (true);

CREATE POLICY "Allow public read orders" ON orders FOR SELECT USING (true);
CREATE POLICY "Allow public insert orders" ON orders FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update orders" ON orders FOR UPDATE USING (true);
CREATE POLICY "Allow public delete orders" ON orders FOR DELETE USING (true);

CREATE POLICY "Allow public read order_items" ON order_items FOR SELECT USING (true);
CREATE POLICY "Allow public insert order_items" ON order_items FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public update order_items" ON order_items FOR UPDATE USING (true);
CREATE POLICY "Allow public delete order_items" ON order_items FOR DELETE USING (true);

GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated, postgres, service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, postgres, service_role;

-- ====================================================================
-- SEED DATA
-- ====================================================================

INSERT INTO categories (name, description) VALUES
('BBQ Meals', 'Hearty and satisfying grilled BBQ combo plates served with fragrant garlic rice and pickled papaya (atchara).'),
('BBQ Skewers', 'Classic street-style skewered meats marinated in our savory-sweet soy and calamansi blend, charcoal-grilled to perfection.'),
('Chicken BBQ', 'Tender, juicy chicken cuts glazed with our signature spicy-sweet basting sauce.'),
('Pork BBQ', 'Authentic Filipino tender pork cuts grilled over coconut charcoal with caramelized glaze.'),
('Drinks & Sides', 'Refreshing beverages, extra sauces, garlic rice, and homemade sides.');

INSERT INTO products (category_id, name, description, price, stock, image, status) VALUES
(2, 'Classic Pork BBQ Skewer', '2 juicy skewers of marinated pork slices grilled over natural charcoal with sweet-savory glaze.', 35.00, 100, 'images/products/pork-bbq.jpg', 'available'),
(3, 'Grilled Chicken Inasal Quarter', 'Leg and thigh quarter marinated in lemongrass, ginger, vinegar, and annatto oil, grilled fresh.', 135.00, 45, 'images/products/chicken-bbq.jpg', 'available'),
(1, 'Signature BBQ Rice Meal', '2 Pork BBQ skewers served with unlimited garlic rice, sunny-side egg, and savory BBQ dipping sauce.', 99.00, 60, 'images/products/bbq-meal.jpg', 'available'),
(4, 'Charcoal Grilled Pork Liempo', 'Thick cut succulent pork belly marinated in special spices and grilled to smoky crisp perfection.', 165.00, 35, 'images/products/pork-bbq.jpg', 'available'),
(3, 'Chicken BBQ Skewer Platter', '5 pieces of tender boneless chicken BBQ skewers basted with our secret house sauce.', 180.00, 30, 'images/products/chicken-bbq.jpg', 'available'),
(1, 'Grilled Liempo Meal Deal', 'Generous slice of grilled liempo served with steamed garlic rice, soup, and atchara.', 175.00, 40, 'images/products/bbq-meal.jpg', 'available'),
(2, 'Isaw Manok (Chicken Intestines)', 'Popular street-food favorite, thoroughly cleaned and barbecued crispy with spicy spiced vinegar.', 25.00, 120, 'images/products/chicken-bbq.jpg', 'available'),
(5, 'Extra Garlic Rice', 'Hot freshly cooked cup of steamed garlic butter rice.', 25.00, 150, 'images/products/bbq-meal.jpg', 'available'),
(5, 'Ice-Cold Coca-Cola (330ml)', 'Refreshing chilled carbonated cola in can.', 35.00, 80, 'images/products/coke.jpg', 'available'),
(5, 'Purified Mineral Water (500ml)', 'Pure drinking water in sealed bottle.', 20.00, 100, 'images/products/water.jpg', 'available');

INSERT INTO users (name, email, password, role, phone, address) VALUES
('BBQ Store Admin', 'admin@bbqhouse.com', '$2b$12$t4UvM0u787YmU34dZ7/e.e/V29qZ.5m4C4i3Yh9G.bQ3QjFhJ5l1S', 'admin', '0912-345-6789', 'Main Branch, BBQ House, Bohol'),
('Juan Dela Cruz', 'customer@bbqhouse.com', '$2b$12$jQjX8o4q4qj1Qe4r6t8y9u0i1o2p3a4s5d6f7g8h9j0k1l2z3x4c5v', 'customer', '0998-765-4321', '123 Rizal Street, Tagbilaran City, Bohol');

INSERT INTO orders (user_id, customer_name, customer_email, customer_phone, delivery_address, order_notes, total_amount, order_status, payment_method, payment_status) VALUES
(2, 'Juan Dela Cruz', 'customer@bbqhouse.com', '0998-765-4321', '123 Rizal Street, Tagbilaran City, Bohol', 'Please include extra spicy BBQ sauce', 184.00, 'preparing', 'cash_on_delivery', 'pending');

INSERT INTO order_items (order_id, product_id, product_name, quantity, price, subtotal) VALUES
(1, 3, 'Signature BBQ Rice Meal', 1, 99.00, 99.00),
(1, 1, 'Classic Pork BBQ Skewer', 1, 35.00, 35.00),
(1, 9, 'Ice-Cold Coca-Cola (330ml)', 1, 35.00, 35.00);
