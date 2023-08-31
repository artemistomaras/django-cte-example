# Django CTE Example

## About

This project demonstrates the usage of Common Table Expressions (CTE) in Django using the package ```django-cte``` and PostgreSQL.

## Installation

### Prerequisites:

* docker
* docker-compose
* python 3.11
* pipenv

Run:

```bash
docker-compose -f config/postgres/docker-compose.yml up -d
pipenv install
python manage.py migrate
python manage.py loaddata fixtures/data.json
python manage.py runserver 0:8000
```

Visit http://localhost:8000/ for project demonstration and example usage.
