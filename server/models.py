from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    serialize_rules = ('-signup', '-created_at', '-updated_at')

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String, nullable = False)
    age = db.Column(db.Integer, db.CheckConstraint( '(age >= 8) and (age <= 18)' ))
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())
    __table_args__ = ( db.CheckConstraint('(age >= 8) and (age <= 18)'), )

    signup = db.relationship('Signup', back_populates = 'camper')
    activity = association_proxy('signup', 'activity')


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    serialize_rules = ('-signup', '-created_at', '-updated_at' )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    signup = db.relationship('Signup', back_populates = 'activity')
    camper = association_proxy('signup', 'camper')

class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    serialize_rules = ('-activity', '-camper')

    id = db.Column(db.Integer, primary_key=True)
    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))
    time = db.Column(db.Integer, db.CheckConstraint('(time >= 1) and (time <= 23)'))
    created_at = db.Column(db.DateTime, server_default = db.func.now())
    updated_at = db.Column(db.DateTime, onupdate = db.func.now())

    __table_args__ = (db.CheckConstraint('(time >= 1) and (time <= 23)'), )

    activity = db.relationship('Activity', back_populates = 'signup')
    camper = db.relationship('Camper', back_populates = 'signup')
    