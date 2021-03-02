from flask_restful import Resource


class RoomsController(Resource):
    def get(self):
        return {'hello': 'world'}
