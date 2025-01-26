import logging
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 1️⃣ Configuration de base pour le logging
logging.basicConfig(
    level=logging.INFO,  # Niveau minimal pour afficher les logs
    format='%(asctime)s - %(levelname)s - %(message)s',  # Format des messages
    handlers=[
        logging.FileHandler("ml_pipeline.log"),  # Logs dans un fichier
        logging.StreamHandler()  # Affichage dans la console
    ]
)
logging.info("Chargement des bibliothèques réussie")
try:
    # 2️⃣ Début de la pipeline ML
    logging.info("Début de la pipeline ML : génération de données synthétiques.")
    X, y = make_classification(n_samples=1000, n_features=20, random_state=42)

    logging.info("Division des données en ensembles d'entraînement et de test.")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 3️⃣ Entraînement du modèle
    logging.info("Entraînement du modèle RandomForest.")
    model = RandomForestClassifier(random_stat=42)
    model.fit(X_train, y_train)

    # 4️⃣ Évaluation du modèle
    logging.info("Prédictions et évaluation des performances.")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    logging.info(f"Précision du modèle : {accuracy:.2f}")

    # 5️⃣ Gestion des anomalies (exemple d'erreur volontaire)
    if accuracy < 0.95:
        logging.warning("Précision inférieure au seuil attendu de 0.95. \n Vérifiez les hyperparamètres.")

except Exception as e:
    logging.error(f"Une erreur s'est produite : {str(e)}", exc_info=True)

logging.info("Fin de la pipeline ML.")
