-- Create table for n_user metric
DROP TABLE IF EXISTS n_user;
CREATE TABLE n_user (
    user_count INTEGER,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for user_registration_growth metric
DROP TABLE IF EXISTS user_registration_growth;
CREATE TABLE user_registration_growth (
    registration_date DATE,
    user_count INTEGER,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for geographical_distribution metric
DROP TABLE IF EXISTS geographical_distribution;
CREATE TABLE geographical_distribution (
    country VARCHAR(100),
    city VARCHAR(100),
    user_count INTEGER,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for customer_lifetime_value metric
DROP TABLE IF EXISTS customer_lifetime_value;
CREATE TABLE customer_lifetime_value (
    user_id INTEGER,
    total_revenue DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for customer_retention_rate metric
DROP TABLE IF EXISTS customer_retention_rate;
CREATE TABLE customer_retention_rate (
    retention_rate DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for top_selling_products metric
DROP TABLE IF EXISTS top_selling_products;
CREATE TABLE top_selling_products (
    product_id INTEGER,
    total_quantity_sold INTEGER,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for revenue_per_category metric
DROP TABLE IF EXISTS revenue_per_category;
CREATE TABLE revenue_per_category (
    category_id INTEGER,
    category_name VARCHAR(100),
    total_revenue DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for average_product_rating metric
DROP TABLE IF EXISTS average_product_rating;
CREATE TABLE average_product_rating (
    product_id INTEGER,
    average_rating DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for product_view_to_purchase_ratio metric
DROP TABLE IF EXISTS product_view_to_purchase_ratio;
CREATE TABLE product_view_to_purchase_ratio (
    product_id INTEGER,
    conversion_ratio DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for total_sales metric
DROP TABLE IF EXISTS total_sales;
CREATE TABLE total_sales (
    total_sales_amount DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for average_order_value metric
DROP TABLE IF EXISTS average_order_value;
CREATE TABLE average_order_value (
    average_order_value DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for basket_size metric
DROP TABLE IF EXISTS basket_size;
CREATE TABLE basket_size (
    average_basket_size DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for order_conversion_rate metric
DROP TABLE IF EXISTS order_conversion_rate;
CREATE TABLE order_conversion_rate (
    conversion_rate DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for monthly_sales_growth metric
DROP TABLE IF EXISTS monthly_sales_growth;
CREATE TABLE monthly_sales_growth (
    month DATE,
    growth_rate DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for payment_method_popularity metric
DROP TABLE IF EXISTS payment_method_popularity;
CREATE TABLE payment_method_popularity (
    payment_method VARCHAR(50),
    payment_count INTEGER,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for payment_success_rate metric
DROP TABLE IF EXISTS payment_success_rate;
CREATE TABLE payment_success_rate (
    success_rate VARCHAR(10),
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for average_payment_time metric
DROP TABLE IF EXISTS average_payment_time;
CREATE TABLE average_payment_time (
    average_payment_time_seconds DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for average_delivery_time metric
DROP TABLE IF EXISTS average_delivery_time;
CREATE TABLE average_delivery_time (
    average_delivery_time_seconds DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for order_cancellation_rate metric
DROP TABLE IF EXISTS order_cancellation_rate;
CREATE TABLE order_cancellation_rate (
    cancellation_rate VARCHAR(10),
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for review_response_rate metric
DROP TABLE IF EXISTS review_response_rate;
CREATE TABLE review_response_rate (
    response_rate VARCHAR(10),
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for top_viewed_products metric
DROP TABLE IF EXISTS top_viewed_products;
CREATE TABLE top_viewed_products (
    product_id INTEGER,
    view_count INTEGER,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for view_to_purchase_conversion_rate metric
DROP TABLE IF EXISTS view_to_purchase_conversion_rate;
CREATE TABLE view_to_purchase_conversion_rate (
    product_id INTEGER,
    conversion_ratio DOUBLE PRECISION,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for product_view_trends metric
DROP TABLE IF EXISTS product_view_trends;
CREATE TABLE product_view_trends (
    view_date DATE,
    view_count INTEGER,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create table for order_status_distribution metric
DROP TABLE IF EXISTS order_status_distribution;
CREATE TABLE order_status_distribution (
    status VARCHAR(50),
    order_count INTEGER,
    calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);