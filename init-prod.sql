

-- Suppression des tables existantes si nécessaire
DO $$ 
BEGIN

    DROP TABLE IF EXISTS product_views CASCADE;
    DROP TABLE IF EXISTS reviews CASCADE;
    DROP TABLE IF EXISTS shipments CASCADE;
    DROP TABLE IF EXISTS payments CASCADE;
    DROP TABLE IF EXISTS order_items CASCADE;
    DROP TABLE IF EXISTS orders CASCADE;
    DROP TABLE IF EXISTS products CASCADE;
    DROP TABLE IF EXISTS categories CASCADE;
    DROP TABLE IF EXISTS addresses CASCADE;
    DROP TABLE IF EXISTS users CASCADE;
    
END $$;



-- Create Categories Table
\echo 'Création de la table categories...'
CREATE TABLE IF NOT EXISTS categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- Create Users Table
\echo 'Création de la table users...'
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    default_address_id INTEGER
);


-- Create Addresses Table
\echo 'Création de la table addresses...'
CREATE TABLE IF NOT EXISTS addresses (
    address_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    street TEXT NOT NULL,
    postal_code VARCHAR(20),
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ajout de la contrainte de clé étrangère pour default_address_id après création de la table addresses
ALTER TABLE users
ADD CONSTRAINT fk_default_address
FOREIGN KEY (default_address_id) 
REFERENCES addresses(address_id) 
ON DELETE SET NULL;

-- Create Products Table
\echo 'Création de la table products...'
CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2) NOT NULL,
    category_id INTEGER REFERENCES categories(category_id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
    billing_address_id INTEGER REFERENCES addresses(address_id) ON DELETE SET NULL,
    shipping_address_id INTEGER REFERENCES addresses(address_id) ON DELETE SET NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(50) NOT NULL
);



-- Create Order Items Table
\echo 'Création de la table order_items...'
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(product_id) ON DELETE SET NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10,2) NOT NULL
);



CREATE TABLE IF NOT EXISTS payments (
    payment_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    payment_method VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    transaction_id VARCHAR(100) UNIQUE NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Create Shipments Table
\echo 'Création de la table shipments...'
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id) ON DELETE CASCADE,
    shipment_date TIMESTAMP,
    tracking_number VARCHAR(100) UNIQUE,
    status VARCHAR(50)
);


-- Create Reviews Table
\echo 'Création de la table reviews...'
CREATE TABLE IF NOT EXISTS reviews (
    review_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE IF NOT EXISTS product_views (
    view_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
    view_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DO $$ 
BEGIN

    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_orders_user_id') THEN
        CREATE INDEX idx_orders_user_id ON orders(user_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_orders_billing_address_id') THEN
        CREATE INDEX idx_orders_billing_address_id ON orders(billing_address_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_orders_shipping_address_id') THEN
        CREATE INDEX idx_orders_shipping_address_id ON orders(shipping_address_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_addresses_user_id') THEN
        CREATE INDEX idx_addresses_user_id ON addresses(user_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_order_items_order_id') THEN
        CREATE INDEX idx_order_items_order_id ON order_items(order_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_order_items_product_id') THEN
        CREATE INDEX idx_order_items_product_id ON order_items(product_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_payments_order_id') THEN
        CREATE INDEX idx_payments_order_id ON payments(order_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_shipments_order_id') THEN
        CREATE INDEX idx_shipments_order_id ON shipments(order_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_reviews_user_id') THEN
        CREATE INDEX idx_reviews_user_id ON reviews(user_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_reviews_product_id') THEN
        CREATE INDEX idx_reviews_product_id ON reviews(product_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_product_views_user_id') THEN
        CREATE INDEX idx_product_views_user_id ON product_views(user_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_product_views_product_id') THEN
        CREATE INDEX idx_product_views_product_id ON product_views(product_id);
    END IF;
   
END $$;


-- Initial Data Insertion
INSERT INTO categories (name, description) 
VALUES
    ('Electronics', 'Electronic devices and gadgets'),
    ('Clothing', 'Apparel and fashion items'),
    ('Home & Kitchen', 'Home appliances and kitchenware'),
    ('Books', 'Fiction and non-fiction books')
ON CONFLICT (name) DO NOTHING;

-- Then users
INSERT INTO users (first_name, last_name, email, password_hash) 
VALUES
    ('John', 'Doe', 'john.doe@example.com', 'password_hash'),
    ('Jane', 'Smith', 'jane.smith@example.com', 'password_hash'),
    ('Abraham','KOLOBOE','abklb27@gmail.com','password_hash')
ON CONFLICT (email) DO NOTHING;

-- Then addresses
INSERT INTO addresses (user_id, country, city, street, postal_code, is_default) 
SELECT user_id, 'USA', 'New York', '123 Main St', '10001', TRUE
FROM users WHERE email = 'john.doe@example.com'
ON CONFLICT DO NOTHING;

INSERT INTO addresses (user_id, country, city, street, postal_code, is_default)
SELECT user_id, 'USA', 'Los Angeles', '456 Elm St', '90001', FALSE
FROM users WHERE email = 'john.doe@example.com'
ON CONFLICT DO NOTHING;

INSERT INTO addresses (user_id, country, city, street, postal_code, is_default)
SELECT user_id, 'Canada', 'Toronto', '789 Oak St', 'M5V 1X7', TRUE
FROM users WHERE email = 'jane.smith@example.com'
ON CONFLICT DO NOTHING;

-- Update Users with Default Address
UPDATE users u
SET default_address_id = a.address_id
FROM addresses a
WHERE u.user_id = a.user_id AND a.is_default = TRUE;

-- Products
INSERT INTO products (name, description, price, category_id) VALUES
('Smartphone', 'Latest model smartphone', 799.99, 1),
('T-Shirt', 'Cotton T-Shirt', 19.99, 2),
('Blender', 'High-speed blender', 149.99, 3),
('Novel', 'Bestselling novel', 14.99, 4);

-- Orders
INSERT INTO orders (user_id, billing_address_id, shipping_address_id, total_amount, status) VALUES
(1, 1, 2, 799.99, 'shipped'),
(2, 3, 3, 19.99, 'delivered');

-- Order Items
INSERT INTO order_items (order_id, product_id, quantity, price) VALUES
(1, 1, 1, 799.99),
(2, 2, 2, 19.99);

-- Payments
INSERT INTO payments (order_id, payment_method, amount, transaction_id) VALUES
(1, 'credit_card', 799.99, 'txn123'),
(2, 'paypal', 19.99, 'txn456');

-- Shipments
INSERT INTO shipments (order_id, shipment_date, tracking_number, status) VALUES
(1, '2023-10-01 10:00:00', 'SH001', 'shipped'),
(2, '2023-09-28 14:30:00', 'SH002', 'delivered');

-- Reviews
INSERT INTO reviews (user_id, product_id, rating, comment) VALUES
(1, 1, 5, 'Great phone, love it!'),
(2, 2, 4, 'Comfortable and stylish.'),
(1, 3, 3, 'Decent blender, but noisy.'),
(2, 4, 5, 'Engaging story, can''t put it down.');

-- Product Views
INSERT INTO product_views (user_id, product_id) VALUES
(1, 1),
(1, 2),
(2, 2),
(2, 4);
