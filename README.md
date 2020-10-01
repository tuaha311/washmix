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

`notifications` - this application responsible for sending SMS and email messages to users and storing historical info about sending.

`orders` - here we store all logic related to the order creation, cart and item management.

`users` - one of the main applications, whole logic of clients, employees management stored here.

`pickups` - logic of request pickups, deliveries

`locations` - main logic of addresses, cities were we present  and zip codes that we support


## Project layout
All applications have a default Django layout - we are trying to stay classic and trying to use default practices.
All views and serializers related to the application incapsulated in application package.
Some of custom views and serializers that doesn't fit logically in application context was saved in `api` package.

Also, we are holding most of complex business logic rules in separate classes called `services`.
And inside views we are using composition approach - instantiating an service and calling methods of service.
In most complex cases it looks very simple and declarative - step by step execution of some methods of service.
For example:
```python
checkout_service = CheckoutService(client, request, invoice)

with atomic():
    checkout_service.save_card_list()
    checkout_service.fill_profile(user)
    checkout_service.create_address(address)
    checkout_service.charge()
```

Looks great isn't it?


## Docs
Most of models are documented with docstrings. 
If you want to see database architecture - please open `models.drawio` at [draw.io](https://draw.io).

REST API documentation can be found at `/openapi/` address.
REST API documentation created in [OpenAPI](https://www.openapis.org) specification. 

OpenAPI can be exported and opened in many editors:
- Insomnia Designer
- Postman 
- Swagger


## How to run worker for background tasks
We are using [dramatiq](https://dramatiq.io) for handling background tasks.

* Install Python dependencies:
  ```bash
  poetry install
  ```
* Go to the `app` folder:
  ```bash
  cd app
  ```
* Run dramatiq:
  ```bash
  dramatiq -v settings.dramatiq
  ```
## How to run periodic scheduler (task emitter) for dramatiq
For this purpose we are using [periodiq](https://gitlab.com/bersace/periodiq).

* Install Python dependencies:
  ```bash
  poetry install
  ```
* Go to the `app` folder:
  ```bash
  cd app
  ```
* Run dramatiq:
  ```bash
  periodiq -v settings.periodiq
  ```

  
## About billing stuff
All prices and money related stuff stored in cents (¢), not in dollars.
In most places, we provide convenient property for amount in dollars.
For example, if we have field `price` in model `Foo`, than we have a property 
called `dollar_price`.


## About initial data (fixtures)
1. To create dump of database in JSON format
```bash
python manage.py dumpdata swap_user_named_email users billing core locations notifications orders pickups -o dump.json
```
2. To load data from dump in JSON format to database
```bash
python manage.py loaddata dump.json
```
