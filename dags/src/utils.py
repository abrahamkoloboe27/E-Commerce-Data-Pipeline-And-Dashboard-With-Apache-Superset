import psycopg2
from psycopg2 import extras
from minio import Minio
import sys
import polars as pl
import io
import logging
from datetime import datetime, timedelta
import time
logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('airflow_logs.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

# MinIO configuration
MINIO_ENDPOINT = "minio:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_BUCKET_RAW = "ecommerce-data-raw"
MINIO_BUCKET_CLEAN = "ecommerce-data-clean"
MINIO_BUCKET_AGGREGATED = "ecommerce-data-aggregated"

def get_minio_client():
    connection = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    return connection

def extract_table(table_name: str, **kwargs):
    execution_date = kwargs['execution_date']
    logging.info(f"Extracting data from {table_name} on {execution_date}")
    date_column_mapping = {
        'users': 'created_at',
        'addresses': 'created_at',
        'products': 'created_at',
        'orders': 'order_date',
        'payments': 'payment_date',
        'shipments': 'shipment_date',
        'reviews': 'review_date',
        'product_views': 'view_date'
    }
    
    # Get the appropriate date column for the table
    date_column = date_column_mapping.get(table_name)
    logging.info(f"Date column for {table_name}: {date_column}")
    # Create PostgreSQL hook
    postgres_connection =  psycopg2.connect(
            dbname="e_commerce_database",
            user="postgres",
            password="postgres",
            host="postgres-prod",
            port="5432"
        )
    
    # Construct query based on whether table has date column
    if date_column:
        query = f"""
            SELECT * FROM {table_name} 
            WHERE DATE({date_column}) = DATE('{execution_date}')
        """
    else:
        # For tables without date columns (like categories), get all records
        query = f"SELECT * FROM {table_name}"

    # Execute query and get data as Polars DataFrame
    df = pl.read_database(query=query, connection=postgres_connection)
    logging.info(f"Extracted {len(df)} records from {table_name}")
    logging.info(f"Extracted data: {df.head()}")
    
    if len(df) > 0:
        # Convert to parquet bytes
        parquet_buffer = io.BytesIO()
        logging.info(f"Writing {len(df)} records to parquet")
        df.write_parquet(parquet_buffer)
        logging.info(f"Finished writing {len(df)} records to parquet")
        parquet_buffer.seek(0)
        
        # Save to MinIO
        minio_client = get_minio_client()
        logging.info(f"Uploading {len(df)} records to MinIO")
        
        # Create bucket if it doesn't exist
        if not minio_client.bucket_exists(MINIO_BUCKET_RAW):
            logging.info(f"Creating bucket {MINIO_BUCKET_RAW}")
            minio_client.make_bucket(MINIO_BUCKET_RAW)
        
        # Define the object path in MinIO
        object_path = f"{table_name}/{table_name}_{execution_date.strftime('%Y-%m-%d')}.parquet"
        logging.info(f"Uploading to {object_path}")
        
        # Upload to MinIO
        try:
            minio_client.put_object(
                bucket_name=MINIO_BUCKET_RAW,
                object_name=object_path,
                data=parquet_buffer,
                length=parquet_buffer.getbuffer().nbytes,
                content_type='application/octet-stream'
            )
            #df.write_parquet(f"dump/{table_name}_{execution_date}.parquet")
        except Exception as e:
            time.sleep(5)
            logging.error(f"Connection failed: {e}. Retrying...")
            minio_client = get_minio_client()
            minio_client.put_object(
                bucket_name=MINIO_BUCKET_RAW,
                object_name=object_path,
                data=parquet_buffer,
                length=parquet_buffer.getbuffer().nbytes,
                content_type='application/octet-stream'
            )
           # df.write_parquet(f"dump/{table_name}_{execution_date}.parquet")
        logging.info(f"Uploaded {len(df)} records to MinIO")
        
        return f"Extracted and saved {len(df)} records from {table_name}"
    else : 
        return f"No data found for {table_name} on {execution_date}"

def load_data_from_minio(table:str , **kwargs):
    execution_date = kwargs['execution_date']
    logging.info(f"Loading data from MinIO for {execution_date}")
    #table = kwargs['table']
    minio_client = get_minio_client()
    object_path = f"{table}/{table}_{execution_date.strftime('%Y-%m-%d')}.parquet"
    logging.info(f"Loading data from {object_path}")
    df = pl.read_parquet(minio_client.get_object(MINIO_BUCKET_RAW, object_path))
    logging.info(f"Loaded table : {table},\n execution_date = {execution_date},\n Data :  {len(df.head())} records from MinIO") 
    return df

def clean_data(table_name: str, execution_date, **kwargs):
    """
    Nettoie les données brutes chargées depuis MinIO
    Effectue les opérations suivantes :
    1. Conversion des timestamps en dates
    2. Gestion des valeurs manquantes
    3. Suppression des doublons
    """
    
    # Chargement des données depuis MinIO
    logging.info(f"Début du nettoyage des données pour {table_name}")
    df = load_data_from_minio(table=table_name, execution_date=execution_date)
    
    # Configuration spécifique par table
    cleaning_config = {
    'categories': {
        'mandatory_columns': ['category_id', 'name'],
        'default_values': {'description': 'No description'},
        'text_columns': ['name', 'description'],
        'unique_constraints': ['name']
    },
    'users': {
        'timestamp_columns': ['created_at'],
        'mandatory_columns': ['user_id', 'email', 'first_name', 'last_name'],
        'foreign_keys': [('default_address_id', 'addresses', 'address_id')]
    },
    'addresses': {
        'timestamp_columns': ['created_at'],
        'mandatory_columns': ['address_id', 'user_id', 'country', 'city', 'street'],
        'default_values': {
            'postal_code': 'N/A',
            'is_default': False
        },
        'geo_columns': {
            'city': {'min_length': 2}
        }
    },
    'products': {
        'timestamp_columns': ['created_at'],
        'mandatory_columns': ['product_id', 'name', 'price'],
        'default_values': {'description': 'No description'},
        'numeric_ranges': {
            'price': {'min': 0.0, 'replace_negative': 0.0}
        },
        'text_columns': ['name', 'description']
    },
    'orders': {
        'timestamp_columns': ['order_date'],
        'mandatory_columns': ['order_id', 'user_id', 'total_amount'],
        'drop_columns': ['billing_address_id', 'shipping_address_id'],
        'numeric_ranges': {
            'total_amount': {'min': 0.0, 'replace_negative': 0.0}
        },
        'status_handling': {
            'allowed_values': ['pending', 'shipped', 'delivered', 'cancelled'],
            'default': 'pending'
        }
    },
    'order_items': {
        'mandatory_columns': ['order_item_id', 'order_id', 'product_id', 'quantity', 'price'],
        'numeric_ranges': {
            'quantity': {'min': 1, 'replace_invalid': 1},
            'price': {'min': 0.0, 'replace_negative': 0.0}
        },
        'foreign_keys': [
            ('order_id', 'orders', 'order_id'),
            ('product_id', 'products', 'product_id')
        ]
    },
    'payments': {
        'timestamp_columns': ['payment_date'],
        'mandatory_columns': ['payment_id', 'order_id', 'amount'],
        'numeric_ranges': {
            'amount': {'min': 0.0, 'replace_negative': 0.0}
        },
        'payment_method_handling': {
            'default': 'credit_card'
        }
    },
    'shipments': {
        'timestamp_columns': ['shipment_date'],
        'mandatory_columns': ['shipment_id', 'order_id', 'tracking_number'],
        'default_values': {'status': 'pending'},
        'status_handling': {
            'allowed_values': ['pending', 'shipped', 'delivered', 'lost'],
            'default': 'pending'
        },
        'tracking_format': 'XXX-XXXX-XXXX'  # Format exemple
    },
    'reviews': {
        'timestamp_columns': ['review_date'],
        'mandatory_columns': ['review_id', 'user_id', 'product_id', 'rating'],
        'default_values': {'comment': 'No comment'},
        'rating_handling': {
            'min': 1,
            'max': 5,
            'replace_outliers': 3
        },
        'text_analysis': ['comment']
    },
    'product_views': {
        'timestamp_columns': ['view_date'],
        'mandatory_columns': ['view_id', 'user_id', 'product_id'],
        'session_handling': {
            'inactivity_threshold': '30m',
            'max_duration': '2h'
        }
    }
    }

    # 1. Conversion des timestamps
    config = cleaning_config.get(table_name, {})
    for col in config.get('timestamp_columns', []):
        if col in df.columns:
            df = df.with_columns(
                pl.col(col).dt.date().alias(f"{col}"),
                pl.col(col).dt.time().alias(f"{col}_time")
            )
            #df = df.drop(col)
            logging.info(f"Converti {col} en date/heure pour {table_name}")

    # 2. Gestion des valeurs manquantes
    # Suppression des lignes avec des colonnes obligatoires manquantes
    if 'mandatory_columns' in config:
        initial_count = len(df)
        df = df.drop_nulls(subset=config['mandatory_columns'])
        logging.info(f"Supprimé {initial_count - len(df)} lignes avec valeurs manquantes critiques")

    # Remplacement des valeurs par défaut
    for col, value in config.get('default_values', {}).items():
        if col in df.columns:
            null_count = df[col].is_null().sum()
            df = df.with_columns(pl.col(col).fill_null(value))
            logging.info(f"Remplacé {null_count} valeurs manquantes dans {col} par {value}")

    # 3. Suppression des doublons
    initial_count = len(df)
    df = df.unique()
    logging.info(f"Supprimé {initial_count - len(df)} doublons")

    # Nettoyage spécifique pour les montants financiers
    if config.get('amount_handling', False):
        df = df.with_columns(
            pl.col('amount').round(2)
        )
        logging.info("Arrondi des montants financiers à 2 décimales")

    # Gestion des colonnes inutiles
    for col in config.get('drop_columns', []):
        if col in df.columns:
            df = df.drop(col)
            logging.info(f"Colonne {col} supprimée")

    logging.info(f"Nettoyage terminé pour {table_name}. Forme finale : {df.shape}")
    
    
    # Convert to parquet bytes
    parquet_buffer = io.BytesIO()
    logging.info(f"Writing {len(df)} records to parquet")
    df.write_parquet(parquet_buffer)
    logging.info(f"Finished writing {len(df)} records to parquet")
    parquet_buffer.seek(0)
    
    # Enregistrement des données nettoyées dans MinIO
    logging.info(f"Enregistrement des données nettoyées pour {table_name}")
    minio_client = get_minio_client()
    if not minio_client.bucket_exists(MINIO_BUCKET_CLEAN):
        logging.info(f"Creating bucket {MINIO_BUCKET_CLEAN}")
        minio_client.make_bucket(MINIO_BUCKET_CLEAN)
            
    # Define the object path in MinIO
    object_path = f"{table_name}/{table_name}_{execution_date.strftime('%Y-%m-%d')}.parquet"
    logging.info(f"Uploading to {object_path}")
        
    # Upload to MinIO
    try:
        minio_client.put_object(
                bucket_name=MINIO_BUCKET_CLEAN,
                object_name=object_path,
                data=parquet_buffer,
                length=parquet_buffer.getbuffer().nbytes,
                content_type='application/octet-stream'
            )
        #df.write_parquet(f"dump/{table_name}_{execution_date}.parquet")
    except Exception as e:
        time.sleep(5)
        logging.error(f"Connection failed: {e}. Retrying...")
        minio_client = get_minio_client()
        minio_client.put_object(
                bucket_name=MINIO_BUCKET_CLEAN,
                object_name=object_path,
                data=parquet_buffer,
                length=parquet_buffer.getbuffer().nbytes,
                content_type='application/octet-stream'
            )
        #df.write_parquet(f"dump/{table_name}_{execution_date}.parquet")
        logging.info(f"Uploaded {len(df.head())} records to MinIO")
    return "Data cleaned and saved to MinIO"




def insert_date_dim(**kwargs):
    execution_date = kwargs['execution_date']
    logging.info(f"Inserting date dimension for {execution_date}")
    date = execution_date.strftime('%Y-%m-%d')
    day = execution_date.day
    month = execution_date.month
    year = execution_date.year
    quarter = (execution_date.month - 1) // 3 + 1
    is_weekend = execution_date.weekday() in [5, 6]
    week_of_year = execution_date.isocalendar()[1] 
    
    # Connect to PostgreSQL
    postgres_connection =  psycopg2.connect(
            dbname="ecommerce_metrics",
            user="postgres",
            password="postgres",
            host="postgres-etl",
            port="5432"
        )
    # Get the last id in the date dimension
    cursor = postgres_connection.cursor()
    cursor.execute("SELECT MAX(time_id) FROM dim_time")
    last_id = cursor.fetchone()[0]
    logging.info(f"Last ID in date dimension: {last_id}")
    if last_id is None:
        last_id = 0
    else:
        last_id += 1
    # Insert into date dimension
    logging.info(f""" Try to insert date dimension for {execution_date} :\n last_id : {last_id} \n""")
    cursor.execute(f"""
        INSERT INTO dim_time (time_id, date, day, month, year, quarter, week_of_year, is_weekend)
        VALUES ({last_id}, '{date}', {day}, {month}, {year}, {quarter}, {week_of_year}, {is_weekend})
        ON CONFLICT (date) DO NOTHING
    """)
    logging.info(f"""Inserted date dimension for {execution_date} :\n last_id : {last_id} 
                 \n date : {date} \n day : {day} \n month : {month} \n year : {year}
                 \n quarter : {quarter} \n week_of_year : {week_of_year} \n is_weekend : {is_weekend}""")
    postgres_connection.commit()
    logging.info(f"Inserted date dimension for {execution_date}")
    return f"Inserted date dimension for {execution_date}"
    
    



def aggregate_daily_data(**kwargs):
    """
    Agrège les données au pas de temps journalier et les enregistre dans MinIO.
    """    
    # Charger les données brutes depuis MinIO
    execution_date = kwargs['execution_date']
    logging.info(f"Début de l'agrégation des données pour {execution_date}")
    minio_client = get_minio_client()
    date_str = execution_date.strftime('%Y-%m-%d')
    
    # Charger les tables nécessaires
    tables = {
        'orders': pl.read_parquet(minio_client.get_object(MINIO_BUCKET_CLEAN, f'orders/orders_{date_str}.parquet')),
        'order_items': pl.read_parquet(minio_client.get_object(MINIO_BUCKET_CLEAN, f'order_items/order_items_{date_str}.parquet')),
        'users': pl.read_parquet(minio_client.get_object(MINIO_BUCKET_CLEAN, f'users/users_{date_str}.parquet')),
        'addresses': pl.read_parquet(minio_client.get_object(MINIO_BUCKET_CLEAN, f'addresses/addresses_{date_str}.parquet')),
        'products': pl.read_parquet(minio_client.get_object(MINIO_BUCKET_CLEAN, f'products/products_{date_str}.parquet')),
        'payments': pl.read_parquet(minio_client.get_object(MINIO_BUCKET_CLEAN, f'payments/payments_{date_str}.parquet')),
        'product_views': pl.read_parquet(minio_client.get_object(MINIO_BUCKET_CLEAN, f'product_views/product_views_{date_str}.parquet')),
        'reviews': pl.read_parquet(minio_client.get_object(MINIO_BUCKET_CLEAN, f'reviews/reviews_{date_str}.parquet')),
        'shipments': pl.read_parquet(minio_client.get_object(MINIO_BUCKET_CLEAN, f'shipments/shipments_{date_str}.parquet')),
    }
    
    logging.info("Calcul des agrégations...")
    # Showing head of tables 
    for table_name, df in tables.items():
        logging.info(f"Table {table_name} shape: {df.shape} \n {df.head()}")
    # Préparation des données de paiement avec user_id
    payments_with_users = (
        tables['payments']
        .join(tables['orders'], on='order_id')
        .select(['user_id', 'amount', 'payment_method', 'payment_date', 'order_id', 'order_date'])
    )
    logging.info(f"Payments with users shape: {payments_with_users.shape} \n {payments_with_users.head()}")
    
    # 1. Fact Sales
    fact_sales = tables['orders']
    logging.info(f"Initial orders: {fact_sales.shape[0]} lignes")
    
    fact_sales = (
        fact_sales
        .join(tables['order_items'], on='order_id', how='left')
        .join(tables['shipments'], on='order_id', how='left')
        .join(payments_with_users, on='order_id', how='left')
        .join(tables['users'], on='user_id', how='left')
        .join(
            tables['addresses'], 
            on='user_id', 
            how='left'
        )
        .join(tables['products'], on='product_id', how='left')
        .group_by([
            'order_date', 
            'product_id', 
            'user_id', 
            'country', 
            'city', 
            'payment_method'
        ])
        .agg([
            pl.sum('quantity').alias('quantity'),
            pl.sum('amount').alias('revenue'),
            pl.first('status').alias('order_status'),
            (
                pl.col('shipment_date').dt.epoch("s") 
                - pl.col('order_date').dt.epoch("s")
            ).alias('delivery_time_seconds')
        ])
        .with_columns(pl.col('order_date').dt.date().alias('date'))
    )
    logging.info(f"Fact Sales final: {fact_sales.shape[0]} lignes")
    
    logging.info(f"Initial Users: {tables['users'].shape[0]} lignes")
    # 2. Fact User Activity
    fact_user_activity = (
        tables['users']
        .join(
            tables['addresses'].filter(pl.col('is_default') == True), 
            on='user_id', 
            how='left'
        )
        .join(
            tables['product_views']
            .group_by('user_id')
            .agg(pl.count().alias('product_views')), 
            on='user_id', 
            how='left'
        )
        .join(
            tables['orders']
            .group_by('user_id')
            .agg(pl.count().alias('purchases')), 
            on='user_id', 
            how='left'
        )
        .join(
            payments_with_users  # Utilisation de payments_with_users ici
            .group_by('user_id')
            .agg(pl.sum('amount').alias('cltv')), 
            on='user_id', 
            how='left'
        )
        .with_columns([
            (pl.col('created_at').dt.date() < execution_date.date() - timedelta(days=30))
            .alias('retention_status'),
            pl.col('product_views').fill_null(0),
            pl.col('purchases').fill_null(0),
            pl.col('cltv').fill_null(0)
        ])
    )
    logging.info(f"Fact User Activity: {fact_user_activity.shape[0]} lignes")
    
    # 3. Fact Product Performance
    logging.info(f"Initial Products: {tables['products'].shape[0]} lignes")
    fact_product_performance = (
        tables['products']
        .join(
            tables['product_views']
            .group_by('product_id')
            .agg(pl.count().alias('views')), 
            on='product_id', 
            how='left'
        )
        .join(
            tables['order_items']
            .group_by('product_id')
            .agg(pl.sum('quantity').alias('purchases')), 
            on='product_id', 
            how='left'
        )
        .join(
            tables['reviews']
            .group_by('product_id')
            .agg(pl.mean('rating').alias('average_rating')), 
            on='product_id', 
            how='left'
        )
        .with_columns([
            pl.col('views').fill_null(0),
            pl.col('purchases').fill_null(0),
            pl.col('average_rating').fill_null(0),
            (pl.col('purchases') / pl.when(pl.col('views') > 0)
             .then(pl.col('views'))
             .otherwise(1))
            .alias('conversion_rate')
        ])
    )
    logging.info(f"Fact Product Performance: {fact_product_performance.shape[0]} lignes")
    
    # 4. Fact Payment Analytics
    logging.info(f"Initial Payments: {payments_with_users.shape[0]} lignes")
    fact_payment_analytics = (
        payments_with_users  # Utilisation de payments_with_users ici aussi
        .group_by(['payment_method', 'payment_date'])
        .agg([
            pl.count().alias('transaction_count'),
            (pl.col('amount') > 0).mean().alias('success_rate'),
            (pl.col('payment_date').dt.epoch('s') - pl.col('order_date').dt.epoch('s'))
            .mean()
            .alias('avg_processing_time')
        ])
        .with_columns(pl.col('payment_date').dt.date().alias('date'))
    )
    logging.info(f"Fact Payment Analytics: {fact_payment_analytics.shape[0]} lignes")
    
    # Enregistrement des données agrégées dans MinIO
    logging.info("Enregistrement des données agrégées dans MinIO...")
    
    for table_name, df in {
        'fact_sales': fact_sales,
        'fact_user_activity': fact_user_activity,
        'fact_product_performance': fact_product_performance,
        'fact_payment_analytics': fact_payment_analytics
    }.items():
        parquet_buffer = io.BytesIO()
        df.write_parquet(parquet_buffer)
        parquet_buffer.seek(0)
        
        if not minio_client.bucket_exists(MINIO_BUCKET_AGGREGATED):
            minio_client.make_bucket(MINIO_BUCKET_AGGREGATED)
            logging.info(f"Création du bucket {MINIO_BUCKET_AGGREGATED}")
        
        object_path = f"{table_name}/{table_name}_{date_str}.parquet"
        minio_client.put_object(
            bucket_name=MINIO_BUCKET_AGGREGATED,
            object_name=object_path,
            data=parquet_buffer,
            length=parquet_buffer.getbuffer().nbytes,
            content_type='application/octet-stream'
        )
        logging.info(f"Données {table_name} enregistrées dans {object_path}, Head : {df.head()}")
        
    
    logging.info(f"Agrégation terminée pour {execution_date}")
    

def get_row_count(cursor, table_name):
    """Récupère le nombre de lignes actuel dans la table"""
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    return cursor.fetchone()[0]
    
def insert_data_in_dimension_table(table_name: str, unique_columns: list, **kwargs):
    """
    Charge les données d'une table de dimension depuis MinIO
    et les insère dans la base analytique en évitant les doublons
    """

    execution_date = kwargs['execution_date']
    date_str = execution_date.strftime('%Y-%m-%d')

    # Configuration des chemins MinIO
    minio_paths = {
        'dim_geography': f"dim_geography/dim_geography_{date_str}.parquet",
        'dim_product': f"dim_product/dim_product_{date_str}.parquet", 
        'dim_user': f"dim_user/dim_user_{date_str}.parquet",
        'dim_payment_method': f"dim_payment_method/dim_payment_method_{date_str}.parquet"
    }

    # Configuration des colonnes obligatoires
    required_columns = {
        'dim_geography': ['country', 'city', 'postal_code'],
        'dim_product': ['product_id', 'name', 'category_id', 'category_name', 'price'],
        'dim_user': ['user_id', 'registration_date', 'country', 'city', 'email', 'first_name', 'last_name'],
        'dim_payment_method': ['payment_method_id', 'method_name']
    }
    not_null_columns = {
    'dim_geography': ['country', 'city', 'postal_code'],
    'dim_product': ['product_id', 'name', 'category_id', 'category_name', 'price'],
    'dim_user': ['user_id', 'registration_date', 'country', 'city', 'email', 'first_name', 'last_name'],
    'dim_payment_method': ['payment_method_id', 'method_name']
    }

    try:
        # Récupération du client MinIO
        minio_client = get_minio_client()
        
        # Récupération du chemin de l'objet
        object_path = minio_paths[table_name]
        
        # Vérification de l'existence du fichier
        if not minio_client.stat_object(MINIO_BUCKET_AGGREGATED, object_path):
            raise FileNotFoundError(f"Fichier {object_path} non trouvé dans MinIO")

        # Chargement depuis MinIO
        response = minio_client.get_object(MINIO_BUCKET_AGGREGATED, object_path)
        df = pl.read_parquet(response.data)
        df = df.drop_nulls(subset=not_null_columns[table_name])

        # Nouveau: Validation des contraintes NOT NULL
        if table_name == 'dim_user':
            null_check = df.select(
                pl.col('email').is_null() |
                pl.col('first_name').is_null() |
                pl.col('last_name').is_null()
            ).to_series().any()
            
            if null_check:
                bad_rows = df.filter(
                    pl.col('email').is_null() |
                    pl.col('first_name').is_null() |
                    pl.col('last_name').is_null()
                )
                logging.error(f"Lignes invalides:\n{bad_rows}")
                raise ValueError("Données invalides avec valeurs NULL")
            
        logging.info(f"Before drop_nulls - shape: {df.shape}")
        logging.info(f"Null counts:\n{df.null_count()}")
        df = df.drop_nulls()
        logging.info(f"After drop_nulls - shape: {df.shape}")
        logging.info(f"Données {table_name} chargées depuis MinIO : {df.shape} , Head : {df.head()}")

        # Vérification des colonnes
        missing_cols = [col for col in required_columns[table_name] if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colonnes manquantes dans {table_name}: {missing_cols}")

        # Connexion à PostgreSQL
        conn = psycopg2.connect(
            dbname="ecommerce_metrics",
            user="postgres",
            password="postgres",
            host="postgres-etl",
            port="5432"
        )
        cursor = conn.cursor()

        # Construction de la requête d'insertion
        columns = ', '.join(required_columns[table_name])
        placeholders = ', '.join(['%s'] * len(required_columns[table_name]))
        conflict_columns = ', '.join(unique_columns)

        query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ON CONFLICT ({conflict_columns}) DO NOTHING
        """


        # Exécution batch
        start_count = get_row_count(cursor, table_name)
        # Convert DataFrame rows to list of tuples
        rows = [tuple(row) for row in df.select(required_columns[table_name]).rows()]
        extras.execute_batch(cursor, query, rows)
        conn.commit()

        # Log des résultats
        end_count = get_row_count(cursor, table_name)
        inserted = end_count - start_count
        logging.info(f"""
            Chargement {table_name} réussi :
            - Lignes traitées : {len(df)}
            - Nouvelles entrées : {inserted}
            - Doublons ignorés : {len(df) - inserted}
        """)

        return inserted

    except Exception as e:
        logging.info(f"Data frame : {df.head()}")
        logging.error(f"Erreur lors du chargement de {table_name} : {str(e)}")
        raise
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()
        return "Data inserted in dimension table"
            
            
def prepare_and_store_dimensions(execution_date: datetime):
    """
    Prépare les tables de dimensions à partir des données brutes
    et les stocke dans MinIO au format Parquet
    """
    date_str = execution_date.strftime('%Y-%m-%d')
    minio_client = get_minio_client()
    # Load required tables
   
    # Configuration des dimensions
    dimensions_config = {
        'dim_geography': {
            'source_tables': ['addresses'],
            'columns': ['country', 'city', 'postal_code'],
            'processing': lambda df: df.select(
                'country', 'city', 'postal_code'
            ).unique()
        },
        'dim_user': {
            'source_tables': ['users', 'addresses'],
            'columns': ['user_id', 'registration_date', 'country', 'city', 'email', 'first_name', 'last_name'],
            'processing': lambda dfs: (
                dfs['users']
                .filter(
                    pl.col('email').is_not_null() & 
                    pl.col('first_name').is_not_null() & 
                    pl.col('last_name').is_not_null()
                )
                .join(
                    # Modification ici : on prend la première adresse pour chaque utilisateur
                    dfs['addresses']
                    .select(['user_id', 'country', 'city'])
                    .group_by('user_id')
                    .agg([
                        pl.col('country').first().alias('country'),
                        pl.col('city').first().alias('city')
                    ]),
                    on='user_id',
                    how='left'
                )
                .select([
                'user_id',
                pl.col('created_at').alias('registration_date'),
                pl.col('country').fill_null('Unknown'),
                pl.col('city').fill_null('Unknown'),
                pl.col('email'),          # Assurez-vous que ces colonnes
                pl.col('first_name'),     # sont bien présentes dans
                pl.col('last_name')       # le DataFrame final
                ])
            )
        },
        'dim_payment_method': {
            'source_tables': ['payments'],
            'columns': ['payment_method_id', 'method_name'],  # Switch order to match table definition
            'processing': lambda df: (
                df.select(pl.col('payment_method').alias('method_name'))
                .unique()
                .with_columns([
                    pl.arange(1, pl.count() + 1).cast(pl.Int32).alias('payment_method_id')
                ])
                .select('payment_method_id', 'method_name')  # Ensure correct column order
            )
        }
    }

    try:
        # Charger les données nécessaires depuis MinIO
        raw_data = {}
        for table in ['users', 'addresses']:
            obj_path = f"{table}/{table}_{date_str}.parquet"
            response = minio_client.get_object(MINIO_BUCKET_RAW, obj_path)
            df = pl.read_parquet(response.data)
            
            # Nouveau: Validation des données critiques
            if table == 'users':
                null_counts = df.select([
                    pl.col('email').is_null().sum(),
                    pl.col('first_name').is_null().sum(),
                    pl.col('last_name').is_null().sum()
                ])
                logging.info(f"Null counts in users: {null_counts}")
            
            raw_data[table] = df
        for dim_cfg in dimensions_config.values():
            for table in dim_cfg['source_tables']:
                if table not in raw_data:
                    object_path = f"{table}/{table}_{date_str}.parquet"
                    response = minio_client.get_object(MINIO_BUCKET_RAW, object_path)
                    raw_data[table] = pl.read_parquet(response.data)
                    logging.info(f"Chargé {table} depuis MinIO - {raw_data[table].shape} Head : {raw_data[table].head()}")
                
        # Traiter chaque dimension
        for dim_name, cfg in dimensions_config.items():
            logging.info(f"Traitement de la dimension {dim_name}...")
            if dim_name == 'dim_user':
                user_df = raw_data['users']
                critical_nulls = user_df.select(
                    pl.col('email').is_null() |
                    pl.col('first_name').is_null() |
                    pl.col('last_name').is_null()
                ).sum().item()
                
                if critical_nulls > 0:
                    raise ValueError(f"{critical_nulls} lignes avec données critiques manquantes dans {dim_name}")
                    
            # Application du traitement
            if len(cfg['source_tables']) == 1:
                df = cfg['processing'](raw_data[cfg['source_tables'][0]])
            else:
                dfs = {t: raw_data[t] for t in cfg['source_tables']}
                df = cfg['processing'](dfs)

            # Validation des colonnes
            missing_cols = [c for c in cfg['columns'] if c not in df.columns]
            if missing_cols:
                logging.error(f"Colonnes dans {dim_name} : {df.columns}")
                logging.info(f"Colonnes requises : {cfg['columns']}")
                logging.error(f"Colonnes manquantes : {missing_cols}")
                raise ValueError(f"Colonnes manquantes dans {dim_name}: {missing_cols}")

            # Stockage dans MinIO
            buffer = io.BytesIO()
            df.write_parquet(buffer)
            buffer.seek(0)
            
            object_path = f"{dim_name}/{dim_name}_{date_str}.parquet"
            if not minio_client.bucket_exists(MINIO_BUCKET_AGGREGATED):
                minio_client.make_bucket(MINIO_BUCKET_AGGREGATED)
                logging.info(f"Création du bucket {MINIO_BUCKET_AGGREGATED}")
            minio_client.put_object(
                MINIO_BUCKET_AGGREGATED,
                object_path,
                buffer,
                length=buffer.getbuffer().nbytes,
                content_type='application/octet-stream'
            )
            logging.info(f"Dimension {dim_name} sauvegardée dans {object_path}")

    except Exception as e:
        logging.error(f"Erreur lors de la préparation des dimensions : {str(e)}")
        raise
    finally:
        logging.info("Dimension preparation process completed")
    
def dimension_pipeline(**kwargs):
    execution_date = kwargs['execution_date']
    prepare_and_store_dimensions(execution_date)
    return "Dimension pipeline success"

def insert_data_in_dim_tables(**kwargs):
    # Define unique constraints for each table
    unique_constraints = {
        'dim_geography': ['country', 'city', 'postal_code'],
        'dim_product': ['product_id'],
        'dim_user': ['user_id'],
        'dim_payment_method': ['payment_method_id']
    }
    
    tables = ['dim_geography', 'dim_product', 'dim_user', 'dim_payment_method']
    for table in tables:
        logging.info(f"Inserting data in {table}")
        insert_data_in_dimension_table(table, unique_constraints[table], **kwargs)
        logging.info(f"Data inserted in {table}")
    logging.info("Data inserted in dimension 'Time'")
    insert_date_dim(**kwargs)
    dimension_pipeline
    logging.info("Data inserted in dimension Time")
    
    logging.info("Data inserted in dimension tables")
    return "Data inserted in dimension tables"

def insert_data_in_fact_table(table_name: str, **kwargs):
    """
    Charge les données d'une table de fait depuis MinIO
    et les insère dans la base analytique
    """

    execution_date = kwargs['execution_date']
    date_str = execution_date.strftime('%Y-%m-%d')
    connection = psycopg2.connect(
        dbname="ecommerce_metrics",
        user="postgres",
        password="postgres",
        host="postgres-etl",
        port="5432"
    )
    cursor = connection.cursor()
    query = f"SELECT time_id FROM dim_time WHERE date = '{date_str}'"
    cursor.execute(query)
    time_id = cursor.fetchone()[0]
    logging.info(f"Time ID for {date_str}: {time_id}")
    # Configuration spécifique aux faits
    fact_config = {
        'fact_sales': {
            'minio_path': f"fact_sales/fact_sales_{date_str}.parquet",
            'required_columns': [
                'time_id', 'product_id', 'user_id', 'geo_id',
                'payment_method_id', 'quantity', 'revenue', 'order_status'
            ],
            'not_null_columns': [
                'time_id', 'product_id', 'user_id', 'quantity', 'revenue'
            ]
        },
        'fact_user_activity': {
            'minio_path': f"fact_user_activity/fact_user_activity_{date_str}.parquet",
            'required_columns': [
                'time_id', 'user_id', 'product_views', 
                'purchases', 'cltv', 'retention_status'
            ],
            'not_null_columns': ['time_id', 'user_id']
        },
        'fact_product_performance': {
            'minio_path': f"fact_product_performance/fact_product_performance_{date_str}.parquet",
            'required_columns': [
                'time_id', 'product_id', 'views', 
                'purchases', 'average_rating', 'conversion_rate'
            ],
            'not_null_columns': ['time_id', 'product_id']
        },
        'fact_payment_analytics': {
            'minio_path': f"fact_payment_analytics/fact_payment_analytics_{date_str}.parquet",
            'required_columns': [
                'payment_method', 'payment_date', 'transaction_count',
                'success_rate', 'avg_processing_time'  
            ],
            'not_null_columns': ['payment_method', 'payment_date']
        }
    }

    try:
        # Validation de la configuration
        if table_name not in fact_config:
            raise ValueError(f"Configuration manquante pour la table de fait {table_name}")
            
        config = fact_config[table_name]
        minio_client = get_minio_client()

        # Chargement depuis MinIO
        response = minio_client.get_object(MINIO_BUCKET_AGGREGATED, config['minio_path'])
        df = pl.read_parquet(response.data)
        df = df.with_columns(pl.lit(time_id).alias("time_id"))
        
        # Nettoyage des données
        df = df.drop_nulls(subset=config['not_null_columns'])
        logging.info(f"Data loaded for {table_name} - shape: {df.shape} , Head : {df.head()}")
        
        # Get geography and payment method IDs
        if table_name == 'fact_sales':
            # Join with dim_geography to get geo_id
            dim_geo = pl.read_database("SELECT geo_id, country, city FROM dim_geography", connection)
            dim_product = pl.read_database("SELECT product_id FROM dim_product", connection)
            
            # First filter out products that don't exist in dim_product
            df = df.join(
                dim_product,
                on='product_id',
                how='inner'
            )
            
            # Then join with geography dimension
            df = df.join(
                dim_geo, 
                left_on=['country', 'city'], 
                right_on=['country', 'city'],
                how='left'
            )
            
            # Join with dim_payment_method to get payment_method_id and handle missing values
            dim_payment = pl.read_database("SELECT payment_method_id, method_name FROM dim_payment_method", connection)
            df = df.join(
                dim_payment,
                left_on='payment_method',
                right_on='method_name',
                how='left'
            )
            # Replace null payment_method_id with default value 1 (assuming 1 is your default payment method)
            df = df.with_columns(pl.col('payment_method_id').fill_null(1))
            logging.info(f"Added foreign keys - shape: {df.shape}, Head: {df.head()}")
        
        # Validation des colonnes
        missing_cols = [col for col in config['required_columns'] if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Colonnes manquantes dans {table_name}: {missing_cols}")

        # Connexion PostgreSQL
        conn = psycopg2.connect(
            dbname="ecommerce_metrics",
            user="postgres",
            password="postgres",
            host="postgres-etl",
            port="5432"
        )
        cursor = conn.cursor()

        # Construction requête spécifique aux faits
        columns = ', '.join(config['required_columns'])
        placeholders = ', '.join(['%s'] * len(config['required_columns']))
        
        query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            ON CONFLICT DO NOTHING
        """

        # Exécution batch avec gestion de volume
        batch_size = 1000
        total_rows = len(df)
        inserted_count = 0
        
        for i in range(0, total_rows, batch_size):
            batch = df.slice(i, batch_size)
            records = [tuple(row) for row in batch.select(config['required_columns']).rows()]
            
            extras.execute_batch(cursor, query, records)
            conn.commit()
            
            inserted_count += cursor.rowcount
            logging.info(f"Lot {i//batch_size + 1} inséré : {cursor.rowcount} lignes")

        logging.info(f"""
            Chargement {table_name} réussi :
            - Lignes traitées : {total_rows}
            - Nouvelles entrées : {inserted_count}
            - Doublons ignorés : {total_rows - inserted_count}
        """)

        return inserted_count

    except Exception as e:
        logging.error(f"Erreur lors du chargement de {table_name} : {str(e)}")
        logging.info(f"Données problématiques : {df.head(5) if 'df' in locals() else 'Aucune donnée'}")
        raise
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()
            
def fact_pipeline(**kwargs) : 
    tables = ['fact_sales', 'fact_user_activity', 'fact_product_performance', 'fact_payment_analytics']
    for table in tables:
        logging.info(f"Inserting data in {table}")
        insert_data_in_fact_table(table, **kwargs)
        logging.info(f"Data inserted in {table}")
    logging.info("Data inserted in fact tables")
    return "Data inserted in fact tables"