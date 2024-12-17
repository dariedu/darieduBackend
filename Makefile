build:
	docker network ls | grep -w mynetwork || docker network create mynetwork #создать сеть, если ее нет
	docker compose build
up:
	mkdir -p ./dariedu/media ./staticfiles
	docker compose up -d
down:
	docker compose down
stop:
	docker compose stop
createsuperuser:
	docker compose exec -ti dariedu-server python manage.py createsuperuser
logs:
	docker compose logs -f dariedu-server

