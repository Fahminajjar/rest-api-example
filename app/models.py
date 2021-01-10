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
