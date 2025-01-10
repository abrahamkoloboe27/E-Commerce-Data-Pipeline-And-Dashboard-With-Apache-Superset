# E-commerce Metrics Pipeline with Airflow

This project is designed to automate the calculation and storage of key e-commerce metrics using Apache Airflow. The pipeline connects to a production database, calculates daily metrics, and stores the results in an analytical database for further analysis and reporting.

## Table of Contents

- [E-commerce Metrics Pipeline with Airflow](#e-commerce-metrics-pipeline-with-airflow)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Features](#features)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage)
  - [Metrics Calculated](#metrics-calculated)
  - [Database Schema](#database-schema)
  - [Airflow DAG](#airflow-dag)
  - [Contributing](#contributing)
  - [License](#license)

## Project Overview

The project consists of the following components:

- **SQL Queries**: Predefined queries to calculate daily e-commerce metrics.
- **Analytical Database Schema**: Tables to store the calculated metrics.
- **Airflow DAG**: A Directed Acyclic Graph (DAG) to automate the daily calculation and storage of metrics.

## Features

- **Daily Metric Calculation**: Automatically calculates metrics for the current day.
- **Data Storage**: Stores calculated metrics in an analytical database with a timestamp.
- **Scalable**: Easily add new metrics by updating the SQL queries and database schema.
- **Error Handling**: Basic error handling to ensure data integrity.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/ecommerce-metrics-pipeline.git
   cd ecommerce-metrics-pipeline
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Airflow**:
   - Follow the [Airflow installation guide](https://airflow.apache.org/docs/apache-airflow/stable/installation.html) to set up Airflow.
   - Configure the Airflow connections `prod_db_conn` and `analytics_db_conn` with your database credentials.

## Configuration

1. **Database Connections**:
   - Ensure that the production and analytical databases are accessible.
   - Configure the connections in Airflow under Admin -> Connections.

2. **Environment Variables**:
   - Set any necessary environment variables for database connections and other configurations.

## Usage

1. **Deploy the DAG**:
   - Place the DAG file in the `dags` directory of your Airflow installation.

2. **Trigger the DAG**:
   - Manually trigger the DAG from the Airflow UI or wait for the scheduled run.

3. **Monitor the DAG**:
   - Use the Airflow UI to monitor the execution of the DAG and view logs.

## Metrics Calculated

The following metrics are calculated daily:

- **User Metrics**:
  - User Registration Growth
  - Geographical Distribution
  - Customer Lifetime Value (CLV)
  - Customer Retention Rate

- **Product and Category Metrics**:
  - Top-selling Products
  - Revenue per Category
  - Average Product Rating
  - Product View to Purchase Ratio

- **Order and Sales Metrics**:
  - Total Sales
  - Average Order Value (AOV)
  - Basket Size
  - Order Conversion Rate
  - Monthly Sales Growth

- **Payment Metrics**:
  - Payment Method Popularity
  - Payment Success Rate
  - Average Payment Time

- **Shipping Metrics**:
  - Average Delivery Time
  - Order Cancellation Rate

- **Review Metrics**:
  - Average Product Rating
  - Review Response Rate

- **Product View Metrics**:
  - Top-viewed Products
  - View-to-Purchase Conversion Rate
  - Product View Trends

- **Operational Metrics**:
  - Order Status Distribution

## Database Schema

The analytical database schema includes tables for each metric, with columns for the metric value, date, and calculation time. Refer to the `init.sql` file for the complete schema.

## Airflow DAG

The Airflow DAG automates the daily calculation and storage of metrics. It dynamically generates tasks for each metric and ensures that the results are stored in the analytical database with the execution date.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeatureName`).
3. Commit your changes (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeatureName`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
