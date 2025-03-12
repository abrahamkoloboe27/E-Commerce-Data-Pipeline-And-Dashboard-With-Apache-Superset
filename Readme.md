# E-commerce Data Pipeline & Analytics Dashboard 🚀📊

[![GitHub stars](https://img.shields.io/github/stars/abrahamkoloboe27/Setup-Databases-With-Docker?style=social)](https://github.com/abrahamkoloboe27/Setup-Databases-With-Docker)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com)

## Project Overview 🎯

A comprehensive data pipeline solution for an e-commerce platform, featuring:
- 🔄 **Data Generation**: Synthetic data creation using Python & Faker
- 🔁 **ETL Pipeline**: Data extraction, transformation, and loading
- 💾 **Data Lake Architecture**: Bronze, Silver, and Gold layer implementation
- 📊 **Analytics & Visualization**: Interactive dashboards with Apache Superset

## Architecture 🏗️

![E-commerce Pipeline Architecture](assets/img/pipeline.png)
*Complete architecture overview of the E-commerce data pipeline*

### Database Designs 💾

#### Production Database Schema
![Production Database Design](assets/img/prod.png)
*OLTP database schema*


#### Analytics Database Schema


![Analytics Database Details](assets/img/etl-1.png)
*Dimension and fact tables structure*

### Pipeline Implementation 🔧

#### Apache Airflow DAG
![DAG Visualization](assets/img/dag.png)
*Data pipeline workflow showing task dependencies*

#### MinIO Data Lake Organization
![MinIO Console](assets/img/minio.png)
*Data Lake structure with Bronze, Silver, and Gold layers*

### Monitoring & Analytics 📊

#### Grafana Monitoring Dashboards
![Monitoring Architecture](assets/img/monitoring.png)
*Monitoring Architecture*

![System Metrics Dashboard](assets/img/minio-grafana-2.png)
*System resource utilization*

![Pipeline Metrics Dashboard](assets/img/minio-grafana-3.png)
*Pipeline execution metrics*

#### Apache Superset Analytics
![E-commerce KPIs Dashboard](assets/img/superset.png)
*Business performance metrics*

![Customer Analytics Dashboard](assets/img/superset-2.png)
*Customer behavior and sales analysis*

### Components Overview 🔍

| Layer | Components | Technologies |
|-------|------------|--------------|
| **Data Source** 📝 | - Data Generator<br>- Production Database | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![Faker](https://img.shields.io/badge/Faker-000000?logo=python&logoColor=white) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white) |
| **Orchestration** ⚙️ | - Workflow Management<br>- Task Scheduling | ![Airflow](https://img.shields.io/badge/Airflow-017CEE?logo=apache-airflow&logoColor=white) |
| **Data Lake** 💧 | - Bronze Layer<br>- Silver Layer<br>- Gold Layer | ![MinIO](https://img.shields.io/badge/MinIO-C72E49?logo=minio&logoColor=white) ![Delta](https://img.shields.io/badge/Delta-003366?logo=delta&logoColor=white) |
| **Data Warehouse** 🏢 | - Analytics Database<br>- Star Schema | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white) |
| **Visualization** 📈 | - Dashboards<br>- KPI Monitoring | ![Superset](https://img.shields.io/badge/Superset-EC6A37?logo=apache&logoColor=white) |
| **Monitoring** 🔍 | - Metrics Collection<br>- Performance Monitoring | ![StatsD](https://img.shields.io/badge/StatsD-4B32C3?logo=graphite&logoColor=white) ![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?logo=prometheus&logoColor=white) ![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white) |

## Technology Stack 🛠️

### Development Tools 💻
| Tool | Version | Purpose |
|------|---------|----------|
| ![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white) Docker | 20.10+ | Containerization |
| ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) Python | 3.10+ | Development |
| ![VS Code](https://img.shields.io/badge/VS_Code-007ACC?logo=visual-studio-code&logoColor=white) VS Code | Latest | IDE |

### Data Processing 🔄
| Tool | Purpose | Badge |
|------|----------|-------|
| Polars | Data transformation | ![Polars](https://img.shields.io/badge/Polars-2A2A2A?logo=python&logoColor=white) |
| Parquet | Data storage | ![Parquet](https://img.shields.io/badge/Parquet-3E9DAB?logo=apache&logoColor=white) |

## Quick Start 🚀

### System Requirements 🖥️
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8 cores |
| RAM | 8GB | 16GB |
| Storage | 20GB | 50GB |
| OS | macOS/Linux | macOS/Linux |

1. **Clone the repository**
```bash
git clone https://github.com/abrahamkoloboe27/e-commerce-pipeline.git
cd e-commerce-pipeline
```

2. **Start the infrastructure**
```bash
docker-compose up -d
```

3. **Initialize the databases**
```bash
docker-compose exec postgres psql -U postgres -f /init-prod.sql
```

### Access Points 🔗

| Service | URL | Credentials | Logo |
|---------|-----|-------------|------|
| Airflow | http://localhost:8080 | admin/admin | ![Airflow](https://img.shields.io/badge/Airflow-017CEE?logo=apache-airflow&logoColor=white) |
| MinIO Console | http://localhost:9001 | minioadmin/minioadmin | ![MinIO](https://img.shields.io/badge/MinIO-C72E49?logo=minio&logoColor=white) |
| Superset | http://localhost:8088 | admin/admin | ![Superset](https://img.shields.io/badge/Superset-EC6A37?logo=apache&logoColor=white) |
| Grafana | http://localhost:3000 | admin/admin | ![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white) |

## Pipeline Workflow 🔄

### Data Flow Summary 📊
| Stage | Input | Output | Technology |
|-------|--------|---------|------------|
| Extraction 📥 | PostgreSQL | MinIO (Bronze) | Airflow, Polars |
| Processing 🔄 | Bronze Layer | Silver Layer | Polars |
| Aggregation 📊 | Silver Layer | Gold Layer | Polars |
| Visualization 📈 | Gold Layer | Dashboards | Superset |

1. **Data Extraction (Bronze Layer)**
   - Daily extraction from PostgreSQL
   - Raw data storage in MinIO

2. **Data Processing (Silver Layer)**
   - Data cleaning and validation
   - Schema standardization
   - Quality checks

3. **Data Aggregation (Gold Layer)**
   - KPI calculation
   - Business metrics computation
   - Analytical views creation

4. **Data Visualization**
   - Real-time dashboards
   - KPI monitoring
   - Business insights

## Monitoring & Observability 📊

- Real-time pipeline monitoring
- Data quality metrics
- System performance dashboards
- Alert configuration

## Future Enhancements 🔮

- [ ] Data quality validation with Great Expectations
- [ ] Advanced ML pipeline integration
- [ ] Real-time streaming capabilities

## About 👨‍💻

Developed by Abraham KOLOBOE. For questions or collaboration:

- 📧 **Email**: abklb27@gmail.com
- 💼 **LinkedIn**: [Abraham KOLOBOE](https://www.linkedin.com/in/abraham-zacharie-koloboe-data-science-ia-generative-llms-machine-learning/)
- 🐙 **GitHub**: [abrahamkoloboe27](https://github.com/abrahamkoloboe27)

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.