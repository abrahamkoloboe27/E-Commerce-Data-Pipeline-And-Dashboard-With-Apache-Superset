from typing import List, Optional
import psycopg2
from psycopg2.errors import UniqueViolation, ForeignKeyViolation, CheckViolation
from psycopg2.extensions import connection
from faker import Faker
from datetime import datetime, timedelta
import random
import logging
import sys
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Configuration du logging
def setup_logging() -> None:
    """Configure le système de logging avec un format détaillé."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('data_generation.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

@retry(
    retry=retry_if_exception_type((UniqueViolation, ForeignKeyViolation)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def insert_with_retry(cur, query: str, params: tuple) -> None:
    """Exécute une requête INSERT avec retry en cas d'erreur."""
    try:
        cur.execute(query, params)
    except (UniqueViolation, ForeignKeyViolation) as e:
        logging.warning(f"Erreur d'insertion: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Erreur inattendue: {str(e)}")
        raise

def connect_to_db() -> connection:
    """Établit une connexion à la base de données."""
    logging.info("Tentative de connexion à la base de données...")
    try:
        conn = psycopg2.connect(
            dbname="e_commerce_database",
            user="postgres",
            password="postgres",
            host="postgres-prod",
            port="5432"
        )
        logging.info("Connexion établie avec succès")
        return conn
    except Exception as e:
        logging.error(f"Erreur de connexion: {str(e)}")
        raise

def generate_categories(conn: connection, num_categories: int = 10) -> None:
    """Génère des catégories."""
    logging.info(f"Génération de {num_categories} catégories")
    cur = conn.cursor()
    fake = Faker()
    successful_inserts = 0
    
    try:
        while successful_inserts < num_categories:
            try:
                category_name = fake.unique.word()
                category_description = fake.text()
                
                cur.execute(
                    "INSERT INTO categories (name, description) VALUES (%s, %s)",
                    (category_name, category_description)
                )
                
                successful_inserts += 1
                
                if successful_inserts % 5 == 0:
                    logging.info(f"Progression catégories: {successful_inserts}/{num_categories}")
                    conn.commit()
                    
            except UniqueViolation:
                logging.warning(f"Catégorie en doublon ignorée: {category_name}")
                conn.rollback()  # Rollback immédiat en cas de doublon
                continue
            except Exception as e:
                logging.error(f"Erreur inattendue lors de l'insertion: {str(e)}")
                conn.rollback()  # Rollback en cas d'erreur inattendue
                continue
                
        conn.commit()  # Commit final
        logging.info("Génération des catégories terminée")
    except Exception as e:
        logging.error(f"Erreur lors de la génération des catégories: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()

def generate_products(conn: connection, num_products: int = 100) -> None:
    """Génère des produits."""
    num_products = random.randint(400, 500)
    logging.info(f"Génération de {num_products} produits")
    cur = conn.cursor()
    fake = Faker()
    try:
        cur.execute("SELECT category_id FROM categories")
        categories = [row[0] for row in cur.fetchall()]
        if not categories:
            raise ValueError("Aucune catégorie trouvée")

        for i in range(num_products):
            product_name = fake.unique.word()
            product_description = fake.text()
            product_price = round(random.uniform(1.0, 1000.0), 2)
            category_id = random.choice(categories)
            date = fake.date_time_between(start_date='-100d', end_date='now')
            try:
                insert_with_retry(
                    cur,
                    "INSERT INTO products (name, description, price, category_id, created_at) VALUES (%s, %s, %s, %s, %s)",
                    (product_name, product_description, product_price, category_id, date)
                )
                if (i + 1) % 50 == 0:
                    logging.info(f"Progression produits: {i + 1}/{num_products}")
                    conn.commit()
            except UniqueViolation:
                logging.warning(f"Produit en doublon ignoré: {product_name}")
                continue
        conn.commit()
        logging.info("Génération des produits terminée")
    except Exception as e:
        logging.error(f"Erreur lors de la génération des produits: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()

def generate_users(conn: connection, num_users: int = 1000) -> None:
    """Génère des utilisateurs."""
    num_users = random.randint(1000, 2000)
    logging.info(f"Génération de {num_users} utilisateurs")
    cur = conn.cursor()
    fake = Faker()
    successful_inserts = 0
    
    try:
        while successful_inserts < num_users:
            try:
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = fake.unique.email()
                password_hash = fake.password()
                created_at = fake.date_time_between(start_date='-100d', end_date='now')
                
                cur.execute(
                    "INSERT INTO users (first_name, last_name, email, password_hash, created_at) VALUES (%s, %s, %s, %s, %s)",
                    (first_name, last_name, email, password_hash, created_at)
                )
                
                successful_inserts += 1
                
                if successful_inserts % 100 == 0:
                    logging.info(f"Progression utilisateurs: {successful_inserts}/{num_users}")
                    conn.commit()
                    
            except UniqueViolation as e:
                logging.warning(f"Email en doublon ignoré: {email}")
                conn.rollback()  # Important: rollback la transaction en cas d'erreur
                continue
            except Exception as e:
                logging.error(f"Erreur inattendue lors de l'insertion: {str(e)}")
                conn.rollback()  # Important: rollback la transaction en cas d'erreur
                continue
                
        conn.commit()
        logging.info("Génération des utilisateurs terminée")
    except Exception as e:
        logging.error(f"Erreur lors de la génération des utilisateurs: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()

def generate_addresses(conn: connection) -> None:
    """Génère des adresses pour les utilisateurs."""
    logging.info("Génération des adresses")
    cur = conn.cursor()
    fake = Faker()
    try:
        cur.execute("SELECT user_id FROM users")
        users = [row[0] for row in cur.fetchall()]
        if not users:
            raise ValueError("Aucun utilisateur trouvé")

        total_users = len(users)
        for i, user_id in enumerate(users):
            num_addresses = random.randint(1, 1000)
            addresses = []
            for _ in range(num_addresses):
                try:
                    country = fake.country()
                    city = fake.city()
                    street = fake.street_address()
                    postal_code = fake.postcode()
                    is_default = False
                    date = fake.date_time_between(start_date='-100d', end_date='now')
                    insert_with_retry(
                        cur,
                        """INSERT INTO addresses 
                           (user_id, country, city, street, postal_code, is_default, created_at) 
                           VALUES (%s, %s, %s, %s, %s, %s, %s ) RETURNING address_id""",
                        (user_id, country, city, street, postal_code, is_default, date)
                    )
                    address_id = cur.fetchone()[0]
                    addresses.append(address_id)
                except Exception as e:
                    logging.warning(f"Erreur lors de l'insertion d'une adresse: {str(e)}")
                    continue

            if addresses:
                default_address_id = random.choice(addresses)
                try:
                    insert_with_retry(
                        cur,
                        "UPDATE users SET default_address_id = %s WHERE user_id = %s",
                        (default_address_id, user_id)
                    )
                except Exception as e:
                    logging.warning(f"Erreur lors de la mise à jour de l'adresse par défaut: {str(e)}")

            if (i + 1) % 100 == 0:
                logging.info(f"Progression adresses: {i + 1}/{total_users} utilisateurs traités")
                conn.commit()

        conn.commit()
        logging.info("Génération des adresses terminée")
    except Exception as e:
        logging.error(f"Erreur lors de la génération des adresses: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()

def generate_orders(conn: connection, start_date: datetime, end_date: datetime) -> None:
    """Génère des commandes."""
    logging.info("Génération des commandes")
    cur = conn.cursor()
    fake = Faker()
    try:
        cur.execute("SELECT user_id FROM users")
        users = [row[0] for row in cur.fetchall()]
        if not users:
            raise ValueError("Aucun utilisateur trouvé")

        total_users = len(users)
        for i, user_id in enumerate(users):
            try:
                cur.execute("SELECT address_id FROM addresses WHERE user_id = %s", (user_id,))
                addresses = [row[0] for row in cur.fetchall()]
                if not addresses:
                    continue

                num_orders = random.randint(0, 10)
                for _ in range(num_orders):
                    billing_address_id = random.choice(addresses)
                    shipping_address_id = random.choice(addresses)
                    order_date = fake.date_time_between(start_date=start_date, end_date=end_date)
                    total_amount = round(random.uniform(10.0, 1000.0), 2)
                    status = random.choice(['pending', 'shipped', 'delivered'])

                    insert_with_retry(
                        cur,
                        """INSERT INTO orders 
                           (user_id, billing_address_id, shipping_address_id, order_date, total_amount, status)
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (user_id, billing_address_id, shipping_address_id, order_date, total_amount, status)
                    )

            except Exception as e:
                logging.warning(f"Erreur lors de la création des commandes pour l'utilisateur {user_id}: {str(e)}")
                continue

            if (i + 1) % 100 == 0:
                logging.info(f"Progression commandes: {i + 1}/{total_users} utilisateurs traités")
                conn.commit()

        conn.commit()
        logging.info("Génération des commandes terminée")
    except Exception as e:
        logging.error(f"Erreur lors de la génération des commandes: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()


    
def generate_order_items(conn: connection) -> None:
    """Génère des articles pour les commandes."""
    logging.info("Génération des articles de commande")
    cur = conn.cursor()
    fake = Faker()
    try:
        cur.execute("SELECT order_id FROM orders")
        orders = [row[0] for row in cur.fetchall()]
        if not orders:
            raise ValueError("Aucune commande trouvée")

        cur.execute("SELECT product_id, price FROM products")
        products = cur.fetchall()
        if not products:
            raise ValueError("Aucun produit trouvé")

        total_orders = len(orders)
        for i, order_id in enumerate(orders):
            num_items = random.randint(1, 10)
            for _ in range(num_items):
                try:
                    product = random.choice(products)
                    product_id, price = product
                    quantity = random.randint(1, 10)
                    
                    insert_with_retry(
                        cur,
                        "INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                        (order_id, product_id, quantity, price)
                    )
                except Exception as e:
                    logging.warning(f"Erreur lors de l'insertion d'un article de commande: {str(e)}")
                    continue

            if (i + 1) % 100 == 0:
                logging.info(f"Progression articles: {i + 1}/{total_orders} commandes traitées")
                conn.commit()

        conn.commit()
        logging.info("Génération des articles de commande terminée")
    except Exception as e:
        logging.error(f"Erreur lors de la génération des articles de commande: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()

def generate_payments(conn: connection) -> None:
    """Génère des paiements pour les commandes."""
    logging.info("Génération des paiements")
    cur = conn.cursor()
    fake = Faker()
    try:
        cur.execute("SELECT order_id, total_amount FROM orders")
        orders = cur.fetchall()
        if not orders:
            raise ValueError("Aucune commande trouvée")

        total_orders = len(orders)
        for i, (order_id, amount) in enumerate(orders):
            try:
                payment_method = random.choice(['credit_card', 'paypal', 'bank_transfer'])
                transaction_id = fake.unique.uuid4()
                payment_date = fake.date_time_between(start_date='-100d', end_date='now')

                insert_with_retry(
                    cur,
                    """INSERT INTO payments 
                       (order_id, payment_method, amount, transaction_id, payment_date) 
                       VALUES (%s, %s, %s, %s, %s)""",
                    (order_id, payment_method, amount, transaction_id, payment_date)
                )
            except UniqueViolation:
                logging.warning(f"Transaction ID en doublon ignorée: {transaction_id}")
                continue
            except Exception as e:
                logging.warning(f"Erreur lors de la création du paiement: {str(e)}")
                continue

            if (i + 1) % 100 == 0:
                logging.info(f"Progression paiements: {i + 1}/{total_orders} commandes traitées")
                conn.commit()

        conn.commit()
        logging.info("Génération des paiements terminée")
    except Exception as e:
        logging.error(f"Erreur lors de la génération des paiements: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()

def generate_shipments(conn: connection) -> None:
    """Génère des expéditions pour les commandes."""
    logging.info("Génération des expéditions")
    cur = conn.cursor()
    fake = Faker()
    try:
        cur.execute("SELECT order_id, order_date FROM orders")
        orders = cur.fetchall()
        if not orders:
            raise ValueError("Aucune commande trouvée")

        total_orders = len(orders)
        for i, (order_id, order_date) in enumerate(orders):
            try:
                shipment_date = fake.date_time_between(start_date=order_date, end_date='now')
                tracking_number = fake.unique.uuid4()
                status = random.choice(['pending', 'shipped', 'delivered'])

                insert_with_retry(
                    cur,
                    """INSERT INTO shipments 
                       (order_id, shipment_date, tracking_number, status) 
                       VALUES (%s, %s, %s, %s)""",
                    (order_id, shipment_date, tracking_number, status)
                )
            except UniqueViolation:
                logging.warning(f"Numéro de suivi en doublon ignoré: {tracking_number}")
                continue
            except Exception as e:
                logging.warning(f"Erreur lors de la création de l'expédition: {str(e)}")
                continue

            if (i + 1) % 100 == 0:
                logging.info(f"Progression expéditions: {i + 1}/{total_orders} commandes traitées")
                conn.commit()

        conn.commit()
        logging.info("Génération des expéditions terminée")
    except Exception as e:
        logging.error(f"Erreur lors de la génération des expéditions: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()

def generate_reviews(conn: connection) -> None:
    """Génère des avis pour les produits commandés."""
    logging.info("Génération des avis")
    cur = conn.cursor()
    fake = Faker()
    try:
        cur.execute("""
            SELECT DISTINCT o.order_id, oi.product_id, o.user_id, o.order_date 
            FROM orders o 
            JOIN order_items oi ON o.order_id = oi.order_id
        """)
        order_products = cur.fetchall()
        if not order_products:
            raise ValueError("Aucune commande avec produits trouvée")

        total_reviews = len(order_products)
        for i, (order_id, product_id, user_id, order_date) in enumerate(order_products):
            if random.random() < 0.7:  # 70% de chance de laisser un avis
                try:
                    review_date = fake.date_time_between(start_date=order_date, end_date='now')
                    rating = random.randint(1, 5)
                    comment = fake.text()

                    insert_with_retry(
                        cur,
                        """INSERT INTO reviews 
                           (user_id, product_id, rating, comment, review_date) 
                           VALUES (%s, %s, %s, %s, %s)""",
                        (user_id, product_id, rating, comment, review_date)
                    )
                except Exception as e:
                    logging.warning(f"Erreur lors de la création de l'avis: {str(e)}")
                    continue

            if (i + 1) % 100 == 0:
                logging.info(f"Progression avis: {i + 1}/{total_reviews} produits traités")
                conn.commit()

        conn.commit()
        logging.info("Génération des avis terminée")
    except Exception as e:
        logging.error(f"Erreur lors de la génération des avis: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()

def generate_product_views(conn: connection, num_views: int = 5000) -> None:
    """Génère des vues de produits."""
    num_views = random.randint(500, 5000)
    logging.info(f"Génération de {num_views} vues de produits")
    cur = conn.cursor()
    fake = Faker()
    try:
        cur.execute("SELECT user_id FROM users")
        users = [row[0] for row in cur.fetchall()]
        if not users:
            raise ValueError("Aucun utilisateur trouvé")

        cur.execute("SELECT product_id FROM products")
        products = [row[0] for row in cur.fetchall()]
        if not products:
            raise ValueError("Aucun produit trouvé")

        for i in range(num_views):
            try:
                user_id = random.choice(users)
                product_id = random.choice(products)
                view_date = fake.date_time_between(start_date='-100d', end_date='now')

                insert_with_retry(
                    cur,
                    "INSERT INTO product_views (user_id, product_id, view_date) VALUES (%s, %s, %s)",
                    (user_id, product_id, view_date)
                )

                if (i + 1) % 500 == 0:
                    logging.info(f"Progression vues: {i + 1}/{num_views}")
                    conn.commit()

            except Exception as e:
                logging.warning(f"Erreur lors de la création de la vue: {str(e)}")
                continue

        conn.commit()
        logging.info("Génération des vues de produits terminée")
    except Exception as e:
        logging.error(f"Erreur lors de la génération des vues de produits: {str(e)}")
        conn.rollback()
        raise
    finally:
        cur.close()

def main() -> None:
    """Fonction principale d'orchestration de la génération des données."""
    setup_logging()
    logging.info("Début du processus de génération des données")
    
    try:
        conn = connect_to_db()
        start_date = datetime.now() - timedelta(days=100)
        end_date = datetime.now()
        
        # Génération des données dans l'ordre des dépendances
        generate_categories(conn)
        generate_products(conn)
        generate_users(conn)
        generate_addresses(conn)
        generate_orders(conn, start_date, end_date)
        generate_order_items(conn)
        generate_payments(conn)
        generate_shipments(conn)
        generate_reviews(conn)
        generate_product_views(conn)
        
        logging.info("Processus de génération des données terminé avec succès")
    except Exception as e:
        logging.error(f"Erreur fatale lors de la génération des données: {str(e)}")
        raise
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()
            logging.info("Connexion à la base de données fermée")

if __name__ == "__main__":
    main()