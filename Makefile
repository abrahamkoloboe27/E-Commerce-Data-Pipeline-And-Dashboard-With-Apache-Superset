data : 
	docker run -d --name postgres-local -e POSTGRES_PASSWORD=postgres -p 1234:5432 postgres -v ./init.sql:./init.sql
	docker exec -it postgres-local psql -U postgres -d e_commerce_database -f ./init.sql
	pip install -r data_genrator/requirements.txt
	python3 data_genrator/genrator.py
# Commandes pour automatiser vos tâches avec Docker Compose  
up:  ## Démarre les services en arrière-plan  
	docker compose up -d  

build:  ## Construit les images Docker  
	docker compose build  

build-up: build up  ## Construit et démarre les services  

down:  ## Arrête les services  
	docker compose down  

down-volumes:  ## Arrête les services et supprime les volumes  
	docker compose down -v  

down-volumes-build-up: down-volumes build up  ## Nettoie, reconstruit et redémarre  
