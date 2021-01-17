class NoDataProvided(Exception):
    pass


class CourseAlreadyExist(Exception):
    pass


errors = {
    'NoDataProvided': {
        'message': "No data provided.",
        'status': 400,
    },
    'CourseAlreadyExist': {
        'message': "Course already exist.",
        'status': 400,
    }
}
