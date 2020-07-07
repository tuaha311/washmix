## How? ##

First of all you need:

* Python (the interpreter) — https://www.python.org/downloads/
* Python Setuptools (initial package installer) — https://pypi.python.org/pypi/setuptools
* PIP (advanced package installer) — https://pypi.python.org/pypi/pip

Initially we have to create virtual environment, here are the steps to create virtual env.

* Browse to directory using terminal and run command "**virtualenv <name_of_env>**"
* Activate environment by browsing to bin folder under newly created env folder and run command "**source activate**"
* Once env is activated, now turn comes to install dependencies.
* Install dependencies from requirement.txt file which exist at root level of the project.
* Run "**pip install -r requirement.txt**"
* djangorestframework-expiring-authtoken==0.1.4
* This will install all of the dependencies into the environment.

It is necessary to have postgresql server running and you must have valid DB and a user created over it.
Currently master branch has user credentials and DB name under settings>dev.py file.
It is up to you to create new DB and user with the existing credentials and name or create of your choice and replace it over the mentioned file.
Before running change **'HOST': 'postgres'** to **'HOST': 'localhost'**

## Note:
if you are using Windows and you have `Docker Toolbox` instead of `Docker Desktop` then all services inside docker containers will be accessable via `192.168.99.100` IP address instead of `localhost` or `127.0.0.1`. If this is the case, change `localhost` with `192.168.99.100` where required.


Next turn comes for running DB migration using following method.
* Run command **python manage.py makemigrations --setting=app.settings.dev**
* This will create migrations folder under models app.
* Before creating migration script make sure migrations folder is not present under models app beforehand.
it is because your are creating new DB so any existing migration might conflict.
* Now turn comes for migrating DB instance. Run **python manage.py migrate models --settings=app.setting.dev**
* If the your are able to successfully run above mentioned 2 commands that means your application has successfully established
connection with running DB instance of postgres over postgresql server.```

Next turn comes from running your application server.
* Before processing with this part of the process you must make sure you are running you server via
activated Environment you have created previously.
* Browse to the root directory of the project using your terminal over you local system.
* Run command **python manage.py runserver --setting=app.settings.dev**
If all of the things are setup correctly you server is ready to serve.

In order to have stripe configured you must have provide stripe api key in the Environment using `STRIPE_API_KEY` key.

# Running App Via PyCharm
1. Setup Database on Docker (this way we don't have to install the db separately)

    - Install Postgres on docker container: 
    
            $ docker run -d -p 5432:5432 --name wm_local -e POSTGRES_PASSWORD=rootroot -e POSTGRES_USER=wm_user -e POSTGRES_DB=wm_local --rm postgres 
       
    - Go into PSQL System and Create new Database
    
            $ docker exec -it wm_local bash
            > psql -U wm_user
            > CREATE DATABASE wm_local;
            > \q
            > exit
            
    - Run migrations
            export DJANGO_SETTINGS_MODULE=app.settings.dev
            uncomment DATABASES inside `settings.dev`
            python manage.py makemigrations
            python manage.py migrate
            python manage.py loaddata app/fixtures/add_dev_user.json
            python manage.py createsu
            python manage.py addauthapp
            
    - Run server (two methods)
    
        - Via PyCharm (Select `Run Server` and click play)
        - Via terminal/command-line: 
            -   `python manage.py runserver --settings=app.settings.dev  0.0.0.0:8000`
            
    - Optional: Download & install a Postgres GUI and login to see all tables, etc.
        - Host: `localhost`
        - User: `wm_user`
        - password: `rootroot`
        - Database: `wm_local`
   