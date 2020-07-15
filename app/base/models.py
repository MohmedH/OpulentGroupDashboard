# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin
from sqlalchemy import Binary, Column, Integer, String, REAL, Date

from app import db, login_manager

from app.base.util import hash_pass

class User(db.Model, UserMixin):

    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(Binary)
    role = Column(String, default='regular')
    name = Column(String)
    created_at = Column(Date)

    def __init__(self, **kwargs):
        setattr(self, 'role', 'regular')
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)
        

    def __repr__(self):
        return str(self.username)

    def u_email(self):
        return self.email

    @property
    def u_role(self):
        return self.role

class UserGraveyard(db.Model):

    __tablename__ = 'Users_Graveyard'

    id = Column(Integer, primary_key=True)
    userID = Column(Integer, unique=True)
    username = Column(String)
    email = Column(String)
    password = Column(Binary)
    role = Column(String, default='regular')
    full_name = Column(String)
    deleted_at = Column(Date)

    def __init__(self, **kwargs):
        setattr(self, 'role', 'regular')
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass( value ) # we need bytes here (not plain str)
                
            setattr(self, property, value)
        

    def __repr__(self):
        return str(self.username)

    def u_email(self):
        return self.email

    @property
    def u_role(self):
        return self.role

@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()

@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None

class Portfolio(db.Model):
    __tablename__ = 'PortfolioMaster'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    name = Column(String)
    invested = Column(Integer)
    weight = Column(REAL)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
                
            setattr(self, property, value)

class Deposit(db.Model):
    __tablename__ = 'DepositRequests'

    id = Column(Integer, primary_key=True)
    userID = Column(Integer)
    date = Column(Date)
    amount = Column(REAL)
    status = Column(String)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]
                
            setattr(self, property, value)
