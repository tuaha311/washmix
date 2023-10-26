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
* Install WeasyPrint [dependencies](https://weasyprint.readthedocs.io/en/stable/install.html):


MacOS:
```bash
brew install python3 cairo pango gdk-pixbuf libffi
```
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
  python app/manage.py migrate --settings settings.dev
  ```
* Run the development server:
  ```bash
  python app/manage.py runserver --settings settings.dev
  ```
* Enjoy!


## Testing
We are using `pytest` for unit testing purposes. It can be executed via following steps:
* Go to `app` folder:
  ```bash
  cd app
  ```
* Run test cases:
  ```bash
  pytest
  ```


## Applications
`api` - REST API views, serializers and common handlers for Django REST Framework.

`billing` - here we store all models related to the balance and cards of user.

`branding` - all stuff that related to the WashMix branding of Admin Panel.

`core` - core application of WashMix project, here we store some common utils, mixins, helper functions and classes. 

`deliveries` - application responsible for logic of request pickups, deliveries.

`locations` - main logic of addresses, cities were we present  and zip codes that we support

`notifications` - this application responsible for sending SMS and email messages to users and storing historical info about sending.

`orders` - here we store all logic related to the order creation, cart and item management.

`subscriptions` - Packages, Subscriptions and related services.

`users` - one of the main applications, whole logic of clients, employees management stored here.


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
You can find all documentation files at `docs` folder:
- `models_architecture.drawio` database architecture - please open it at [draw.io](https://draw.io).
- `twilio_import_flow.json` Twilio Scenario Flow export JSON, you can export it in [Twilio Console](https://twilio.com)
- `twilio_scenario_flowchart.drawio` Twilio Flow Flowchart - please open it at [draw.io](https://draw.io).

REST API documentation can be found at `/openapi/` address.
REST API documentation created in [OpenAPI](https://www.openapis.org) specification. 

OpenAPI can be exported and opened in many editors:
- Insomnia Designer
- Postman 
- Swagger

## About User models
We have a corresponding models that can authenticate in WashMix:
- Client (our WashMix application clients, that can purchase subscription and make pickups.)
- Employee (WashMix stuff that handles orders, that comes for request pickups and etc.)

Client and Employee has One-to-One relation with User.

Why we choose One-to-One relation? Because we have 2 different models (Client, Employee) and both of them
can use Django Authentication system to login, signup and etc - we just need to link models with One-to-One User and our authentication
system will work for both of models (Client, Employee).

One-to-One relation is most simple and robust solution for this case (when we have 2 different models that can
use authentication system). If we choose approach with custom user model - we need to implement full authentication cycle 
for both models (Client, Employee). 


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

At the moment, we have 3 models that responsible for invoicing:
  - `Subscription`, we charge user for active subscription
  - `Basket`, we charge for items in WashMix laundry
  - `Delivery`, charge for logistics costs
  
Corresponding to models, we have a wrapper around this models called `containers`:
  - `SubscriptionContainer`
  - `BasketContainer`
  - `QuantityContainer`
  - `RequestContainer`
  - `OrderContainer`
  
Test card list:
```bash
4242 4242 4242 4242 - success
4000 0025 0000 3155 - requires authentication
4000 0000 0000 9995 - declined
```


## About initial data (fixtures)
1. To create dump of database in JSON format
```bash
python manage.py dumpdata --natural-foreign -o dump.json contenttypes auth to_named_email billing core deliveries locations notifications orders subscriptions users
```
2. To load data from dump in JSON format to database
```bash
python manage.py loaddata dump.json
```

We have predefined test in fixture users with emails:
* payc@washmix.com
* gold@washmix.com
* platinum@washmix.com
* superadmin@washmix.com
* admin@washmix.com
* laundress@washmix.com
* driver@washmix.com

All test users have same password `helloevrone`


## Notes
For weekday storing in database and when working in codebase we are using integers starting from 1 (Mon) to 7 (Sun).
In Python code you can use `.isoweekday` method for access to this value.


## Signals
We have `post_save` signal for Delivery model that sends SMS on Client's number with
delivery information.


## Twilio
Attributes for `Sent to Flex` widget that copied from YouTube:
```json
{"name": "{{trigger.message.ChannelAttributes.from}}", "channelType": "{{trigger.message.ChannelAttributes.channel_type}}", "channelSid": "{{trigger.message.ChannelSid}}"}
```

Valid body for working with Twilio Flex Proxy Service
```json
{"message": "{{trigger.message.Body}}", "phone": "{{trigger.message.ChannelAttributes.from}}"}
```

Valid body for working with Twilio Studio
```json
{"message": "{{trigger.message.Body}}", "phone": "{{trigger.message.From}}"}
```

## Heroku DB Backups
https://devcenter.heroku.com/articles/heroku-postgres-backups#creating-a-backup

Run this via heroku cli
```bash
heroku pg:backups:schedules --app washmix-back
heroku pg:backups --app washmix-back
```


## CHANGES MADE BY AMIR
Install pyenv
- on Mac: `brew install pyenv`
- pyenv version -> 2 (run `pyenv update` if needed)
- Install Python 3.9.12 (this is Apple Chip compatible)
- `pyenv install 3.9.12`
- `pyenv local 3.9.12`
- `brew install pango` (this is required by WeasyPrint)

1. Upgrade all packages to latest (DjangoV4, Python 3.9, etc.)
2. Rename `branding/apps.py` to `branding/admin_apps.py` [see this for more info](https://github.com/PacktPublishing/Web-Development-with-Django/issues/5#issuecomment-914195589)


### Copy of requirements.txt
```
Django==2.*
Pillow>7.2.0
WeasyPrint==52.*
djoser==2.0.3
django-cors-headers==3.9.*
django-debug-toolbar==3.2.*
django-filter==2
django-jet==1.0.*
django-robots==3.1.0
django-swap-user==0.3.4
django-templated-mail==1.1.1
djangoql==0.14.*
djangorestframework==3.12
djangorestframework-simplejwt==4.6
drf-writable-nested>=0.6.0
drf-yasg==1.20
dramatiq[redis,watch]==1.9
environs==8.0.0
fabric3==1.14.post1
gunicorn==20.0.4
isort==5.4.2
mypy==0.790
netaddr==0.8.0
phonenumbers==8.12.7
psycopg2-binary==2.8.5
pytest==5.4.3
pytest-django==3.10.0
pyyaml==5.3.*
redis==3.5.*
requests==2.*
requests-oauthlib==1.0.0
sendgrid==6.4.*
sentry-sdk==0.16.*
social-auth-app-django==3.1.0
stripe==2.*
twilio==6.*
uritemplate~=3.0.1
```