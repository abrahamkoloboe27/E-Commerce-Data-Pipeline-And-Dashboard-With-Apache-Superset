-- Dimensions
CREATE TABLE IF NOT EXISTS dim_time (
    time_id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    week_of_year INTEGER NOT NULL,
    is_weekend BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_geography (
    geo_id SERIAL PRIMARY KEY,
    country VARCHAR(100),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    UNIQUE(country, city, postal_code)
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category_id INTEGER NOT NULL,
    category_name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_user (
    user_id INTEGER PRIMARY KEY,
    registration_date DATE NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_payment_method (
    payment_method_id SERIAL PRIMARY KEY,
    method_name VARCHAR(50) NOT NULL UNIQUE
);

-- Faits
CREATE TABLE IF NOT EXISTS fact_sales (
    sale_id SERIAL PRIMARY KEY,
    time_id INTEGER NOT NULL REFERENCES dim_time(time_id),
    product_id INTEGER NOT NULL REFERENCES dim_product(product_id),
    user_id INTEGER NOT NULL REFERENCES dim_user(user_id),
    geo_id INTEGER NOT NULL REFERENCES dim_geography(geo_id),
    payment_method_id INTEGER NOT NULL REFERENCES dim_payment_method(payment_method_id),
    quantity INTEGER NOT NULL,
    revenue DECIMAL(10,2) NOT NULL,
    order_status VARCHAR(50) NOT NULL,
    delivery_time_seconds INTEGER
);

CREATE TABLE IF NOT EXISTS fact_user_activity (
    activity_id SERIAL PRIMARY KEY,
    time_id INTEGER NOT NULL REFERENCES dim_time(time_id),
    user_id INTEGER NOT NULL REFERENCES dim_user(user_id),
    geo_id INTEGER NOT NULL REFERENCES dim_geography(geo_id),
    product_views INTEGER NOT NULL DEFAULT 0,
    purchases INTEGER NOT NULL DEFAULT 0,
    cltv DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    retention_status BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_product_performance (
    performance_id SERIAL PRIMARY KEY,
    time_id INTEGER NOT NULL REFERENCES dim_time(time_id),
    product_id INTEGER NOT NULL REFERENCES dim_product(product_id),
    views INTEGER NOT NULL DEFAULT 0,
    purchases INTEGER NOT NULL DEFAULT 0,
    conversion_rate DECIMAL(5,2) NOT NULL,
    average_rating DECIMAL(3,2) NOT NULL,
    stock_level INTEGER
);

CREATE TABLE IF NOT EXISTS fact_payment_analytics (
    payment_id SERIAL PRIMARY KEY,
    time_id INTEGER NOT NULL REFERENCES dim_time(time_id),
    payment_method_id INTEGER NOT NULL REFERENCES dim_payment_method(payment_method_id),
    transaction_count INTEGER NOT NULL,
    success_rate DECIMAL(5,2) NOT NULL,
    avg_processing_time DECIMAL(10,2) NOT NULL
);

-- Indexes pour les requêtes analytiques
CREATE INDEX IF NOT EXISTS idx_fact_sales_time ON fact_sales(time_id);
CREATE INDEX IF NOT EXISTS idx_fact_sales_product ON fact_sales(product_id);
CREATE INDEX IF NOT EXISTS idx_fact_user_geo ON fact_user_activity(geo_id);
CREATE INDEX IF NOT EXISTS idx_fact_payment_method ON fact_payment_analytics(payment_method_id);
CREATE INDEX IF NOT EXISTS idx_geography_country ON dim_geography(country);
CREATE INDEX IF NOT EXISTS idx_geography_city ON dim_geography(city);
CREATE INDEX IF NOT EXISTS idx_product_category ON dim_product(category_id);
CREATE INDEX IF NOT EXISTS idx_user_registration ON dim_user(registration_date);