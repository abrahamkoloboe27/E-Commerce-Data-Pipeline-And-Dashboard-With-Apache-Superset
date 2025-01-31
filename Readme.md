# E-commerce Data Pipeline & Analytics Dashboard

## 📊 Aperçu du projet
Ce projet est une solution complète de traitement de données pour une plateforme e-commerce, implémentant :
- Génération de données synthétiques
- Pipeline de traitement ELT/ETL
- Data Lake organisé (Bronze-Silver-Gold)
- Data Warehouse avec modélisation dimensionnelle
- Tableau de bord analytique

## 🛠 Architecture technique
![Schéma d'architecture](lien_vers_image_schéma.png) *[Optionnel : Ajouter un diagramme d'architecture]*

### Technologies clés :
- **Génération données** : Python + Faker
- **Orchestration** : Apache Airflow
- **Traitement données** : Polars
- **Stockage** : 
  - Data Lake : Minio (S3-compatible)
  - Data Warehouse : PostgreSQL
- **Visualisation** : Apache Superset

## 🔄 Workflow du pipeline
1. **Extraction des données**
   - Connecteur PostgreSQL → Minio (Bronze)
   - Extraction incrémentale (par date) ou totale

2. **Transformation des données** (via Polars)
   - **Couche Silver** :
     - Nettoyage des données
     - Filtrage des anomalies
     - Standardisation des formats
   
   - **Couche Gold** :
     - Agrégations métiers
     - Calculs de KPI
     - Préparation pour l'analytique

3. **Chargement dans le Data Warehouse**
   - Modèle en étoile (Star Schema)
   - Tables de faits :
     - Transactions
     - Interactions utilisateurs
     - Stocks
   - Tables de dimensions :
     - Produits
     - Clients
     - Dates
     - Fournisseurs

4. **Visualisation**
   - Dashboard interactif avec Apache Superset
   - Métriques principales :
     - CA par période
     - Performances produits
     - Comportement clients
     - Analyses géographiques

## 📂 Structure des données
### Data Lake (Minio)
```
minio/
├── bronze/
│   ├── raw_sales/
│   ├── raw_users/
│   └── ... (tables brutes)
├── silver/
│   ├── cleaned_sales/
│   ├── enriched_users/
│   └── ... (données traitées)
└── gold/
    ├── sales_kpi/
    ├── customer_lifetime_value/
    └── ... (agrégats métiers)
```

### Data Warehouse (PostgreSQL)
- Schéma `dim_*` pour les dimensions
- Schéma `fact_*` pour les faits
- Vues matérialisées pour les requêtes fréquentes

## 🚀 Démarrage rapide
### Prérequis
- Docker + Docker-compose
- Python 3.10+

### Installation
1. Cloner le dépôt
```bash
git clone https://github.com/votre-repo/ecommerce-pipeline.git
cd ecommerce-pipeline
```

2. Démarrer l'infrastructure
```bash
docker-compose up -d
```

3. Configurer Airflow
```bash
airflow db init
airflow users create --username admin --password admin --role Admin --email admin@example.com
```

4. Lancer le pipeline
```bash
airflow dags unpause ecommerce_pipeline
```

## 🔍 Monitoring
- **Airflow** : http://localhost:8080
- **Minio** : http://localhost:9001
- **Superset** : http://localhost:8088
- **PostgreSQL** : 
  - Prod: port 5432
  - Analytics: port 5433

## 📈 Améliorations futures
- Implémentation de tests de qualité des données (Great Expectations)
- Ajout de mécanismes de rejeu de données
- Intégration de Machine Learning (recommandations)
- Monitoring détaillé avec Prometheus/Grafana

## 📚 Documentation complémentaire
- [Specifications techniques](docs/SPECS.md)
- [Guide de déploiement](docs/DEPLOYMENT.md)
- [Modèle de données](docs/DATA_MODEL.md)
