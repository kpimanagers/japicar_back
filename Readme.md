# Co2 Backend

## Getting Started

- Build and run the development environment:

```bash
docker-compose -f docker-compose.dev.yml up --build
```

- Deploy to production:

```bash
docker-compose up --build
```

## Running migrations

Running new migration

```bash
alembic revision --autogenerate -m ""
```

Undo last migration

```bash
alembic downgrade -1
```

Updating migrations

```bash
alembic upgrade head
```

## Commands docker

command open bash container

```bash
docker exec -it mycontainer bash
```

command removes the stopped containers and dangling images

```bash
docker rm -f $(docker ps -qa)
```

remove all the containers:

```bash
docker rmi -f $(docker images -aq)
```

watch status all containers (memory etc...)

```bash
docker stats --all
```
