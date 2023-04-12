from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy.exc import IntegrityError

from models import db, Camper, Activity, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)


db.init_app(app)

api = Api(app)


class Campers(Resource):
    def get(self):
        campers = [c.to_dict() for c in Camper.query.all()]
        return make_response(campers, 201)

    def post(self):
        data = request.get_json()
        try:
            new_camper = Camper(name = data['name'], age = data['age'])
            db.session.add(new_camper)
            db.session.commit()
        
        except IntegrityError:
            db.session.rollback()
            return make_response({'errors': '[validation errors]'}, 400)

        return make_response(new_camper.to_dict(), 201)

api.add_resource(Campers, "/campers")

class CampersId(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()

        if camper == None:
            return make_response({'error': 'camper not found'}, 400)

        return make_response(camper.to_dict(only = ('name', 'id', 'age', 'activity')), 201)

    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        data = request.get_json()

        try:
            for key in data.keys():
                setattr(camper, key, data[key])

            db.session.add(camper)
            db.session.commit()
        
        except IntegrityError:
            db.session.rollback()
            return make_response({'error' : 'invalid data'})
        
        return make_response(camper.to_dict(), 201)


api.add_resource(CampersId, "/campers/<int:id>")

class Activities(Resource):
    def get(self):
        activities = [a.to_dict() for a in Activity.query.all()]
        return make_response(activities, 201)

api.add_resource(Activities, "/activities")

class ActivitiesId(Resource):
    def get(self, id):
        activity = Activity.query.filter_by(id=id).first()

        if activity == None:
            return make_response({'error' : 'activity not found'}, 400)

        return make_response(activity.to_dict(), 201)
    
    def delete(self, id):
        
        for s in Signup.query.all():
            if s.activity_id == id:
                db.session.delete(s)
                db.session.commit()
        
        activity = Activity.query.filter_by(id=id).first()
        
        if activity == None:
            return make_response({'error' : 'activity not found'})

        db.session.delete(activity)
        db.session.commit()

        return make_response({}, 200)

api.add_resource(ActivitiesId, "/activities/<int:id>")


class Signups(Resource):
    def get(self):
        signups = [s.to_dict() for s in Signup.query.all()]
        return make_response(signups, 201)

    def post(self):
        data = request.get_json()
        try:
            new_signup = Signup(time = data['time'], camper_id = data['camper_id'], activity_id = data['activity_id'])
            db.session.add(new_signup)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return make_response({"errors": ["validation errors"]}, 400)

        return make_response(new_signup.activity.to_dict(), 200)

api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
