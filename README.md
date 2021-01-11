# How to Build REST APIs? The Unknown Hero Under The Hood
This is an example for my Medium article to show how to build a RESTful API using Flask microframework.

## Requirements
* We'll use Python3.x so make sure that you have [Python3.x](https://www.python.org/) installed on your machine
* We'll use [SQLite](https://www.sqlite.org/index.html) as it's easy for this example purpose but you can use whatever database you like
* We'll create a virtual Python environment for our application using [virtualenv](https://docs.python-guide.org/dev/virtualenvs/#lower-level-virtualenv)

## Steps for creating a REST API

### Step 1: Set up the application

* First, create a directory for this application called `course_service` , the structure of your application will look like this:

```
course_service
|-- app
    |-- __init__.py     # App entry point
    |-- api.py          # API endpoints
    |-- models.py       # App models
    |-- configs.py      # App configurations
|-- manage.py           # Command line interface
|-- requirements.txt    # App dependencies and requirements
```

* Next, create a virtual environment for the application called `venv`:

```bash
$ cd course_service
$ virtualenv -p python3 venv
```

* Activate the virtual environment:

```bash
$ source venv/bin/activate
```

* Now add the application requirements to the `requirements.txt` file. The good thing about Flask that it's a micro-library and you can add extensions to your application as you need.

We'll be using `Flask` microframework, `Flask-Restful` extension to add support for REST APIs, `Flask-SQLAlchemy` extension to add support for SQLAlchemy, `Flask-Script` to provide support for writing command-line scripts, `Flask-Migrate` to handle SQLAlchemy database migrations for the Flask application, `marshmallow` (ORM/ODM/framework-agnostic library) to convert complex data types, such as objects, to and from native Python datatypes, and `marshmallow-sqlalchemy` because Flask-SQLAlchemy integration requires it to be installed:

```
Flask==1.1.2
Flask-RESTful==0.3.8
Flask-SQLAlchemy==2.4.4
flask-marshmallow==0.14.0
Flask-Script==2.0.6
Flask-Migrate==2.5.3
marshmallow==3.10.0
marshmallow-sqlalchemy==0.24.1
```

### Step 2: Install application requirements

Download and install all application requirements that we added to the `requirements.txt` file:

```bash
$ pip install -r requirements.txt
```

### Step 3: Configure the application

Add the following configurations to the `app/configs.py` module, configurations might be database configs, debug mode, and so on:

```python3
import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True
```

### Step 4: Create the application entry point

The `app/__init__.py` module will be the entry point of our application, it initializes a new Flask application with the given configurations and it defines resource routing.

```python3
from flask import Flask, Blueprint
from flask_restful import Api
from app.api import CourseAPI

# API object
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Routing
api.add_resource(CourseAPI, '/courses/<int:course_id>', '/courses')

# Creating Flask app
def create_app(configs):
    app = Flask(__name__)
    app.config.from_object(configs)
    app.register_blueprint(api_bp, url_prefix='/api')
    from app.models import db
    db.init_app(app)
    return app


if __name__ == '__main__':
    app = create_app('config')
    app.run(debug=True)
```

### Step 5: Create the models

In the `app/models.py` module, create a simple `Course` model (resource) that has an id as the primary key and a name field. `CourseSchema` uses marshmallow to define the output format (serialization/deserialization) of a course object.

```python3
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields

db = SQLAlchemy()
ma = Marshmallow()

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)

class CourseSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
```

### Step 6: Create API endpoints

Flask-Rest provides a `Resource` class that defines routing from any given URL to the intended HTTP method. Define `CourseAPI` in the `app/api.py` module:

```python3
from flask import request
from flask_restful import Resource
from app.models import db, Course, CourseSchema
from marshmallow.exceptions import ValidationError

course_schema = CourseSchema()
courses_schema = CourseSchema(many=True)


class CourseAPI(Resource):
    def get(self, course_id=None):
        if course_id:
            course = Course.query.filter_by(id=course_id).first_or_404()
            return course_schema.dump(course), 200
        else:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))

            pagination = Course.query.paginate(
                page=page, per_page=per_page)
                
            return {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'items': courses_schema.dump(pagination.items)
            }, 200

    def post(self):
        req_data = request.get_json()
        if not req_data:
            return {'message': 'No data provided'}, 400

        try:
            data = course_schema.load(req_data)
        except ValidationError as e:
            errors = e.args[0]
            return errors, 400

        course = Course.query.filter_by(name=data['name']).first()
        if course:
            return {'message': 'Course already exist'}, 400
        course = Course(name=data['name'])

        db.session.add(course)
        db.session.commit()

        return course_schema.dump(course), 201

    def put(self, course_id):
        course = Course.query.filter_by(id=course_id).first_or_404()

        req_data = request.get_json()
        if not req_data:
            return {'message': 'No data provided'}, 400

        try:
            data = course_schema.load(req_data)
        except ValidationError as e:
            errors = e.args[0]
            return errors, 400

        course.name = data['name']
        db.session.commit()

        return course_schema.dump(course), 200

    def delete(self, course_id):
        Course.query.filter_by(id=course_id).delete()
        db.session.commit()
        return {}, 204
```

### Step 7: Create the manage script

The `manage.py` module provides you with a command-line interface to manipulate the database (initializing the database, making model migrations, and running migrations), run an interactive shell, and run the application server.

```python3
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app.models import db
from app import create_app

app = create_app('config')

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
```

### Step 8: Run the application server

First, initialize the database for the application:

```bash
$ python manage.py db init
```

Next, generate migration scripts (Python scripts) for the new models with detected changes, as in our case, a migration script to create the courses table:

```bash
$ python manage.py db migrate
```

Run the generated migrations to apply them to the database:

```bash
$ python manage.py db upgrade
```

Finally, you are good to go:

```bash
$ python manage.py runserver
```

Try to manipulate a course resource using the CRUD-operations. You can use the basic CURL command or any other tool like Postman:
* **[GET, POST]:** `localhost:5000/api/courses`
* **[GET, PUT, DELETE]:** `localhost:5000/api/courses/{ID}`
