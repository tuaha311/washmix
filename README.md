# WashMix


## Project inital setup

* Clone the repo 
  ```bash
  git clone git@github.com:evrone/washmix-back.git
  ```
* Install [poetry](https://python-poetry.org/docs/#installation).
* Install [Docker](https://www.docker.com/get-started).
* Install [docker-compose](https://docs.docker.com/compose/install/).
* Install [Python >= 3.7.5](https://www.python.org/downloads/).
* Install [pre-commit](https://pre-commit.com).
* Checkout to `dev` branch:
  ```bash
  git checkout dev
  ```
* Install Python dependencies:
  ```bash
  poetry install
  ```
* Install pre-commit hooks:
  ```bash
  pre-commit install
  ```
* Setup infrastructure:
  ```bash
  docker-compose up -d
  ```
* Create file `.env` at `app/settings` level with following content:
  ```
  SECRET_KEY=foobar
  SIMPLE_JWT_SIGNING_KEY=spam
  DJANGO_SETTINGS_MODULE=settings.dev
  ```
* Enter into virtualenv
  ```
  poetry shell
  ```
* Run migrations:
  ```
  python manage.py migrate --settings settings.dev
  ```
* Run the development server:
  ```bash
  python manage.py runserver --settings settings.dev
  ```
* Enjoy!


## Applications
`billing` - here we store all models related to the balance and cards of user.

`core` - core models of washmix project.

`notifications` - this application responsible for sending SMS and email messages to users.

`orders` - here we store all logic related to the order creation, cart and item management.

`users` - one of the main applications, whole logic of clients, employees management stored here.


## Docs
Most of models are documented with docstrings. 
If you want to see database architecture - please open `models.drawio` at [draw.io](https://draw.io).

REST API documentation can be found at `/openapi/` address.
REST API documentation created in [OpenAPI](https://www.openapis.org) specification. 

OpenAPI can be exported and opened in many editors:
- Insomnia Designer
- Postman 
- Swagger
