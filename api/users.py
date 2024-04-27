from flask_restful import Resource, reqparse

parser = reqparse.RequestParser()
parser.add_argument("username", required=True)
parser.add_argument("password", password=True)


class RegisterRes(Resource):
    def post(self):
        args = parser.parse_args()
