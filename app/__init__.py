from flask import Flask, Blueprint
from flask_restful import Api
from flask_migrate import Migrate
from app.api import CourseAPI
from app.errors import errors


# API object
api_bp = Blueprint('api', __name__)
api = Api(api_bp, errors=errors)


# Routing
api.add_resource(CourseAPI, '/courses/<int:course_id>', '/courses')


# Creating Flask app
def create_app(configs='app.configs'):
    app = Flask(__name__)
    app.config.from_object(configs)
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.models import db
    db.init_app(app)
    Migrate(app=app, db=db)

    return app


if __name__ == '__main__':
    app = create_app('app.configs')
    app.run(debug=True)
