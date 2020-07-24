# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""
import random
import string
from flask import jsonify, session, render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user
)

from app import db, login_manager
from app.base import blueprint
from app.base.forms import LoginForm, CreateAccountForm
from app.base.models import User, Portfolio, PasswordReset
import app.home.emailsend
from app.base.util import verify_pass, hash_pass


@blueprint.route('/')
def route_default():
    #print(current_user.u_role)
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/error-<error>')
def route_errors(error):
    return render_template('errors/{}.html'.format(error))

## Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()
        
        # Check the password
        if user and verify_pass( password, user.password):

            login_user(user)
            return redirect(url_for('base_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template( 'login/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template( 'login/login.html',
                                    form=login_form)

    return redirect(url_for('home_blueprint.index'))

@blueprint.route('/setup', methods=['GET', 'POST'])
def create_first_user():
    create_account_form = CreateAccountForm(request.form)

    user = User.query.filter_by(id=1).first()

    if request.method == 'POST':          
        if user:
           #print("THIS END POINT IS NOT LONGER VALID")
           redirect(url_for('base_blueprint.route_default'))
        else:
            user = User(**request.form)
            user.role = 'admin'
            user.name = 'Admin'
            #user.created_at = 'n/a'
            defaultPort = {'email':user.email,'invested':0, 'name':user.name, 'weight':0.0, 'gains':0, 'losses':0, 'gltotal':0, 'withdrawls':0, 'total':0}
            protfolio = Portfolio(**defaultPort)
            
            db.session.add(user)
            db.session.add(protfolio)
            db.session.commit()

    if user:
        return redirect(url_for('base_blueprint.route_default'))
    else:
        return render_template( 'login/register.html', form=create_account_form)

'''
@blueprint.route('/create_user', methods=['GET', 'POST'])
def create_user():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username  = request.form['username']
        email     = request.form['email'   ]

        user = User.query.filter_by(username=username).first()
        if user:
            return render_template( 'login/register.html', msg='Username already registered', form=create_account_form)

        user = User.query.filter_by(email=email).first()
        if user:
            return render_template( 'login/register.html', msg='Email already registered', form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        # create portfolio default row with $0 invested amount
        defaultPort = {'email':user.email,'invested':0}
        protfolio = Portfolio(**defaultPort)
        db.session.add(protfolio)
        db.session.commit()

        return render_template( 'login/register.html', msg='User created please <a href="/login">login</a>', form=create_account_form)

    else:
        return render_template( 'login/register.html', form=create_account_form)
'''

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

@blueprint.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    #do reset stuff here!
    login_form = LoginForm(request.form)

    if request.method == 'POST':
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                code = get_random_string(6)
                pR = PasswordReset.query.filter_by(uuid=user.uuid).first()
                if pR:
                    pR.code = code
                    db.session.commit()
                else:
                    pR = PasswordReset()
                    pR.code = code
                    pR.uuid = user.uuid
                    db.session.add(pR)
                    db.session.commit()
                fgTemplate = render_template('forgotpass.html',code=code, url=request.base_url)
                app.home.emailsend.send_forgotpass__mail.delay(user.email,fgTemplate)
                return render_template( 'login/forgotpass.html',msg=request.form['email'], errM="If your email was valid, check your email for the link!")
            else:
                return render_template( 'login/forgotpass.html',msg=request.form['email'], errM="If your email was valid, check your email for the link!")
        except:
            return render_template( 'login/forgotpass.html', errM="Something Went Wrong!")

    
    return render_template( 'login/forgotpass.html')

@blueprint.route('/reset_password/<code>', methods=['GET', 'POST'])
def reset_password_code(code):
    #do reset stuff here!
    login_form = LoginForm(request.form)

    try:
        pR = PasswordReset.query.filter_by(code=code).first()

        if pR:
            pass
        else:
            return render_template('errors/404.html'), 404
    except:
        return render_template('errors/500.html'), 500


    if request.method == 'POST':
        try:
            password = request.form['password']
            vpassword = request.form['verify']

            if password != vpassword:
                return render_template('login/resetpass.html', errM="Please make sure the passwords match, and is atleast 8 characters!")
                #return redirect(url_for('base_blueprint.reset_password_code', code=code))

            user = User.query.filter_by(uuid=pR.uuid).first()
            pwd = hash_pass(password)
            user.password = pwd

            db.session.delete(pR)
            db.session.commit()
            
            return redirect(url_for('base_blueprint.route_default'))
        except:
            return render_template('login/resetpass.html', errM="Something Went Wrong!")

    
    return render_template('login/resetpass.html')
    #return redirect(url_for('base_blueprint.route_default'))

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

'''
@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'
'''

## Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('errors/403.html'), 403

@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('errors/403.html'), 403

@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500
