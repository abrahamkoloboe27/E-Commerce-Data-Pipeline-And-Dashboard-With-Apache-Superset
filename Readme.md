# E-commerce Data Pipeline & Analytics Dashboard 🚀📊

[![GitHub stars](https://img.shields.io/github/stars/abrahamkoloboe27/Setup-Databases-With-Docker?style=social)](https://github.com/abrahamkoloboe27/Setup-Databases-With-Docker)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![MinIO](https://img.shields.io/badge/MinIO-C72E49?logo=minio&logoColor=white)](https://min.io/)
[![Apache Superset](https://img.shields.io/badge/Superset-EC6A37?logo=apache&logoColor=white)](https://superset.apache.org/)
[![Apache Parquet](https://img.shields.io/badge/Parquet-3E9DAB?logo=apache&logoColor=white)](https://parquet.apache.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![StatsD](https://img.shields.io/badge/StatsD-4B32C3?logo=graphite&logoColor=white)](https://github.com/statsd/statsd)
[![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![Apache Airflow](https://img.shields.io/badge/Airflow-017CEE?logo=apache-airflow&logoColor=white)](https://airflow.apache.org/)


## 🌟 Project Overview

A comprehensive data engineering platform for e-commerce including:
- 🧩 **Synthetic data generation** with Python Faker
- 🏗️ **ETL Pipeline** orchestrated by Apache Airflow
- 📦 **Structured Data Lake** (Bronze/Silver/Gold)
- 📊 **Interactive dashboards** with Apache Superset
- 🔍 **Real-time monitoring** via Grafana

## 🏗️ Global Architecture
![Global Architecture](assets/img/pipeline.png)

### 📊 Key Components
| Component | Technologies | Emoji |
|-----------|--------------|-----------|
| **Orchestration** | Apache Airflow, Docker | ⚙️ |
| **Storage** | MinIO, PostgreSQL, Parquet | 💾 |
| **Transformation** | Python, Polars | 🔄 |
| **Visualization** | Apache Superset | 📈 |
| **Monitoring** | Prometheus, Grafana, cAdvisor | 📊 |

## 🗃️ Database Schemas

### 🛒 Production Database (OLTP)
![OLTP Schema](assets/img/prod.png)  
*Relational structure optimized for transactions*

| Characteristic | Details |
|-----------------|---------|
| **Type** | Relational (PostgreSQL) |
| **Tables** | - users<br>- addresses<br>- categories<br>- products<br>- orders<br>- order_items<br>- payments<br>- shipments<br>- reviews<br>- product_views |
| **Indexes** | - idx_orders_user_id<br>- idx_orders_billing_address_id<br>- idx_orders_shipping_address_id<br>- idx_addresses_user_id<br>- idx_order_items_order_id<br>- idx_order_items_product_id<br>- idx_payments_order_id<br>- idx_shipments_order_id<br>- idx_reviews_user_id<br>- idx_reviews_product_id<br>- idx_product_views_user_id<br>- idx_product_views_product_id |
| **Optimization** | Normalization, Referential integrity constraints |

### 📈 Analytics Database (OLAP)
![OLAP Schema](assets/img/etl.png)  
*Star schema for business analysis*

| Characteristic | Details |
|-----------------|---------|
| **Type** | Data Warehouse (PostgreSQL) |
| **Schema** | Star Schema |
| **Tables** | Fact_Sales, Fact_User_Activity, Fact_Product_Performance, Fact_Payment_Analytics, Dim_Products, Dim_Time, Dim_Geography, Dim_User, Dim_Payment_Method |
| **Indexes** | - idx_fact_sales_time<br>- idx_fact_sales_product<br>- idx_fact_user_geo<br>- idx_fact_payment_method<br>- idx_geography_country<br>- idx_geography_city<br>- idx_product_category<br>- idx_user_registration |

## 🛠️ Pipeline Components

### 📦 Data Generation
![Data Generator Architecture](assets/img/data-generator.png)  
*Synthetic data generation workflow with Python Faker*

### 🔄 Orchestration Workflow
![🔄 Data Flow Overview](assets/img/data-flow.png)  
*Complete data flow from source to dashboards*

![Airflow DAG](assets/img/dag.png)  
*ETL task management with Apache Airflow*

| Step | Tools | Output |
|-------|--------|--------|
| Extraction | Faker, PostgreSQL | 🗃️ Bronze Layer (MinIO) |
| Transformation | Polars, Python | 🧹 Silver Layer (Parquet) |
| Loading | SQL, dbt | 🏆 Gold Layer (PostgreSQL) |

## 📊 Monitoring & Visualization

### 🖥️ Operational Dashboarding
![Superset Dashboard](assets/img/superset.png)  
*Real-time business KPIs with Apache Superset*

| Metric | Tool | Emoji |
|----------|-------|-----------|
| Sales | Superset | 📈 |
| Performance | Grafana | 📉 |
| Logs | Prometheus | 📋 |

### 🔍 Monitoring Stack
![Monitoring Stack](assets/img/monitoring.png)  
*Container and metrics monitoring*

| Component | Function | Dashboard |
|-----------|----------|-----------|
| **cAdvisor** | Docker Monitoring | ![Grafana cAdvisor](assets/img/grafana-cadvisor.png) |
| **Postgres-Exporter** | PostgreSQL Metrics | ![Grafana Postgres](assets/img/grafana-postgres.png) |
| **StatsD-Exporter** | Airflow Metrics | ![Grafana Airflow](assets/img/grafana-airflow.png) |
| **MinIo Server** | MinIO Metrics |![Grafana MinIO](assets/img/minio-grafana.png) |

## 🚀 Quick Start

### 📋 Prerequisites
| Component | Minimum | Recommended |
|-----------|---------|------------|
| CPU | 4 cores | 8 cores |
| RAM | 8GB | 16GB |
| Storage | 50GB SSD | 100GB NVMe |

```bash
git clone https://github.com/your-repo.git
cd e-commerce-pipeline
make build  # Build Docker images
make up  # Start containers
make build-up  # Build and start containers
make down  # Stop and remove containers
make down-volumes  # Remove containers and volumes
make down-volumes-build-up  # Remove containers, volumes, and build new images
```
### 🔗 Service Access
| Service | URL | Credentials | Port |
|---------|-----|------------|------|
| Airflow | http://localhost:8080 | admin/admin | 8080 |
| MinIO | http://localhost:9001 | minioadmin/minioadmin | 9001 |
| Superset | http://localhost:8088 | admin/admin | 8088 |
| Grafana  | http://localhost:3000 | grafana/grafana | 3000 |

## 📌 Features Highlights

| Feature | Technology | Benefit |
|---------|------------|---------|
| Hierarchical Data Lake | MinIO + Parquet | 🏷️ Raw/transformed data structuring |
| Modular ETL | Airflow + Python | 🔄 Workflow reproducibility |
| Unified Monitoring | Grafana + Prometheus | 📊 360° performance view |

## 📜 License & Contact

📄 **License**: [MIT](LICENSE)  
📧 **Contact**: [abklb27@gmail.com](mailto:abklb27@gmail.com)  
👨💻 **Author**: [Abraham Koloboe](https://linkedin.com/in/your-profile)


**[⬆ Back to top](#e-commerce-data-pipeline--analytics-dashboard-)**  
*✨ Made with passion for data engineering!*
