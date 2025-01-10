data : 
	docker run -d --name postgres-local -e POSTGRES_PASSWORD=postgres -p 1234:5432 postgres -v ./init.sql:./init.sql
	docker exec -it postgres-local psql -U postgres -d e_commerce_database -f ./init.sql
	pip install -r data_genrator/requirements.txt
	python3 data_genrator/genrator.py
up : 
	docker compose up -d
build : 
	docker compose build
build-up : build up
down : 
	docker compose down
down-volumes : 
	docker compose down -v