# E-commerce Data Pipeline & Analytics Dashboard 🚀📊

[![GitHub stars](https://img.shields.io/github/stars/abrahamkoloboe27/Setup-Databases-With-Docker?style=social)](https://github.com/abrahamkoloboe27/Setup-Databases-With-Docker)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com)



## Aperçu du Projet

Ce projet propose une solution complète de traitement de données pour une plateforme e-commerce, couvrant la **génération de données synthétiques**, le **pipeline de traitement ELT/ETL**, le stockage dans un **Data Lake/ Warehouse** et la visualisation via **Apache Superset**.




## Architecture Technique 🏗️

### Schéma d'architecture
*Insérez ici un diagramme ou une capture illustrant l’architecture globale (Data Lake, Data Warehouse, Airflow, Superset, etc.).*

![Diagramme d'architecture](./docs/images/architecture_diagram.png)



## Technologies Utilisées

| **Composant**               | **Technologie**                                                     | **Icône/Image**                           |
|-----------------------------|----------------------------------------------------------------------|-------------------------------------------|
| **Génération de Données**   | Python, Faker                                                        | ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) |
| **Orchestration**           | Apache Airflow                                                       | ![Airflow](https://img.shields.io/badge/Airflow-017CEE?logo=apache-airflow&logoColor=white) |
| **Traitement**              | Polars                                                               | ![Polars](https://img.shields.io/badge/Polars-2A2A2A?logo=python&logoColor=white)  |
| **Stockage (Data Lake)**    | Minio (S3-compatible)                                                | ![Minio](https://img.shields.io/badge/Minio-00ADEF?logo=minio&logoColor=white) |
| **Data Warehouse**          | PostgreSQL                                                           | ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?logo=postgresql&logoColor=white) |
| **Visualisation**           | Apache Superset                                                      | ![Superset](https://img.shields.io/badge/Superset-EC6A37?logo=apache-superset&logoColor=white) |
| **Monitoring**              | Grafana, Prometheus (prévu)                                            | ![Grafana](https://img.shields.io/badge/Grafana-F46800?logo=grafana&logoColor=white)  |



## Workflow du Pipeline 🔄

Le pipeline s'organise en 4 étapes principales :

| **Étape**               | **Description**                                                                                                             | **Technologies / Outils**                                      |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| **Extraction**          | Récupération des données depuis PostgreSQL vers le Data Lake (Minio – couche Bronze).                                        | PostgreSQL, Minio                                              |
| **Transformation**      | Nettoyage, filtrage, agrégations et calcul des KPI. Les données passent par une couche Silver (nettoyées) puis Gold (agrégées). | Polars                                                         |
| **Chargement**          | Insertion des données transformées dans le Data Warehouse en utilisant un modèle en étoile (Star Schema).                     | PostgreSQL, Vues matérialisées                                   |
| **Visualisation**       | Création d’un dashboard interactif pour suivre les performances (CA, produits, clients, etc.).                              | Apache Superset                                                |

*Astuce : Ajoutez une capture du dashboard Superset pour une meilleure illustration.*

![Dashboard Superset](./docs/images/superset_dashboard.png)



## Focus sur Apache Airflow 🐍⏰

Le dossier `dags/` contient la définition des workflows Airflow. En particulier, le fichier `dags/ecommerce_pipeline.py` orchestre l’ensemble du pipeline :

- **Définition du DAG**  
  Le DAG est configuré pour s’exécuter à une fréquence définie (ex : quotidiennement) et comprend plusieurs tâches :
  - **Extraction** : Récupérer les données depuis PostgreSQL.
  - **Transformation** : Utiliser Polars pour nettoyer et transformer les données.
  - **Chargement** : Insérer les données dans le Data Warehouse.
  
- **Graphique du DAG**  
  *Insérez ici une capture du graphique de tâches d’Airflow pour visualiser l’ordonnancement du pipeline.*

![Graphique du DAG Airflow](./docs/images/airflow_dag.png)



## Démarrage Rapide 🚀

### Prérequis

- **Docker** & **Docker-compose**
- **Python 3.10+**

### Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/abrahamkoloboe27/E-Commerce-Data-Pipeline-And-Dashboard-With-Apache-Superset.git
   cd E-Commerce-Data-Pipeline-And-Dashboard-With-Apache-Superset
   ```

2. **Démarrer l'infrastructure**
   ```bash
   docker-compose up -d
   ```

3. **Configurer Airflow**
   ```bash
   airflow db init
   airflow users create --username admin --password admin --role Admin --email admin@example.com
   ```

4. **Lancer le pipeline**
   ```bash
   airflow dags unpause ecommerce_pipeline
   ```



## Monitoring & Accès 🖥️

| **Service**       | **URL**                        | **Port**     |
|-------------------|--------------------------------|--------------|
| **Airflow**       | [http://localhost:8080](http://localhost:8080)       | 8080         |
| **Minio**         | [http://localhost:9001](http://localhost:9001)       | 9001         |
| **Superset**      | [http://localhost:8088](http://localhost:8088)       | 8088         |
| **PostgreSQL**    | - Prod : `localhost:5432`      | 5432 (Prod)  |
|                   | - Analytics : `localhost:5433` | 5433         |



## Améliorations Futures 🔮

- **Tests de Qualité des Données** : Intégrer [Great Expectations](https://greatexpectations.io) pour automatiser la validation des données.
- **Rejeu de Données** : Mettre en place des mécanismes permettant de rejouer le pipeline en cas d'erreur.
- **Machine Learning** : Ajouter des modules de recommandation et d'analyse prédictive.
- **Monitoring Avancé** : Utiliser Prometheus et Grafana pour un suivi détaillé des performances du pipeline.



## Ressources Complémentaires

- [Guide de Déploiement](./docs/deployment_guide.md)
- [Specifications Techniques](./docs/technical_specs.md)
- [Modèle de Données](./docs/data_model.png)


## About

Ce projet a été développé pour démontrer une solution complète de pipeline de données pour une plateforme e-commerce. Pour plus d’informations ou pour toute question, n’hésitez pas à me contacter :

- **Email** : abklb27@gmail.com
- **LinkedIn** : [Abraham KOLOBOE](https://www.linkedin.com/in/abraham-zacharie-koloboe-data-science-ia-generative-llms-machine-learning/)
