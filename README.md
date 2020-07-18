# [The Opulent Group - User Dashboard]

<br />

## Dashboard Features:

- SQLite, PostgreSQL, SQLAlchemy ORM
- Alembic (DB schema migrations)
- Modular design with **Blueprints**
- Session-Based authentication (via **flask_login**)
- Forms validation
- Deployment scripts: Docker, Gunicorn / Nginx
- UI Kit: **[Material Dark Dashboard](https://flask-dashboard-material-dark.appseed.us/login)** (Free version) provided by **Creative-Tim**
- **MIT License**
<br />

## Dashboard Links


<br />

## Local setup for dev / testing
*It is reccommended to do step on line 49 below. This will help view traffic and requests in terminal.

```bash
$ # Get the code
$ git clone https://github.com/app-generator/flask-dashboard-material-dark.git
$ cd flask-dashboard-material-dark
$
$ # Virtualenv modules installation (Unix based systems)
$ virtualenv --no-site-packages env
$ source env/bin/activate
$
$ # Virtualenv modules installation (Windows based systems)
$ # virtualenv --no-site-packages env
$ # .\env\Scripts\activate
$
$ # Install modules - SQLite Database
$ pip3 install -r requirements.txt
$
$ # OR with PostgreSQL connector
$ # pip install -r requirements-pgsql.txt
$
$ # Set the FLASK_APP environment variable
$ (Unix/Mac) export FLASK_APP=run.py
$ (Windows) set FLASK_APP=run.py
$ (Powershell) $env:FLASK_APP = ".\run.py"
$
$ # Set up the DEBUG environment
$ # (Unix/Mac) export FLASK_ENV=development
$ # (Windows) set FLASK_ENV=development
$ # (Powershell) $env:FLASK_ENV = "development"
$
$ # Start the application (development mode)
$ # --host=0.0.0.0 - expose the app on all network interfaces (default 127.0.0.1)
$ # --port=5000    - specify the app port (default 5000)  
$ flask run --host=0.0.0.0 --port=5000
$
$ #In a new terminal, make sure you're in (env) and in the same folder as where you started the app
$ #Also make sure you have Redis instance running on port 6379
$
$ celery -A app.celery worker --loglevel=info
$
$
$ #Also in config you will need a postgres db running on localhost for dev 
$ #'postgresql://localhost/TOG' it will look for the DB TOG, if you do not have this created, please make one of change this in config.py
$
$
$ # Access the dashboard in browser: http://127.0.0.1:5000/
```

Any Changes To The DB will require Alembic Migrations:
```
$ flask db migrate  # To detect automatically all the changes.
$ flask db upgrade  # To apply all the changes.

# The above commands will save, and update the changes to the user model.
# Because we do not commit DB changes, for these to be applied run this..

$ flask db stamp head  # To set the revision in the database to the head, without performing any migrations. You can change head to the required change you want.

#Followed by the first two commands to bring it all up to date.
```


<br />

## Docker execution

The application can be easily excuted in a docker container. The steps:

> Get the code

```bash
$ git clone https://github.com/app-generator/flask-dashboard-material-dark.git
$ cd flask-dashboard-material-dark
```

>You will have to go in and change the server_name in the /nginx/{name}.config file. If you would like to access via localhost, or IP of the machine (i.e without domain name) just ommit this line

> Start the app in Docker

```bash
$ sudo docker-compose pull && sudo docker-compose build && sudo docker-compose up -d
```

*If you used server_name and it is set up properly, you will be able to access this site directly at that domain.

Visit `http://localhost` or `127.0.0.1` in your browser. The app should be up & running. We expose port 5005 For the application internally, and expose port 80 to the internet. All request come in at port 80 and go through NGINX and are passed along to app:5005 then handeled my gunicorn.
