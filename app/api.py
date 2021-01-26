from flask import request
from flask_restful import Resource
from app import errors
from app.models import db, Course, CourseSchema
from marshmallow.exceptions import ValidationError


course_schema = CourseSchema()


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
                'items': course_schema.dump(pagination.items, many=True)
            }, 200

    def post(self):
        req_data = request.get_json()
        if not req_data:
            raise errors.NoDataProvided

        try:
            data = course_schema.load(req_data)
        except ValidationError as e:
            errors_dict = e.args[0]
            return errors_dict, 400

        course = Course.query.filter_by(name=data['name']).first()
        if course:
            raise errors.CourseAlreadyExist

        course = Course(name=data['name'])

        db.session.add(course)
        db.session.commit()

        return course_schema.dump(course), 201

    def put(self, course_id):
        course = Course.query.filter_by(id=course_id).first_or_404()

        req_data = request.get_json()
        if not req_data:
            raise errors.NoDataProvided

        try:
            data = course_schema.load(req_data)
        except ValidationError as e:
            errors_dict = e.args[0]
            return errors_dict, 400

        course.name = data['name']
        db.session.commit()

        return course_schema.dump(course), 200

    def delete(self, course_id):
        Course.query.filter_by(id=course_id).delete()
        db.session.commit()
        return {}, 204
