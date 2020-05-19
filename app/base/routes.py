# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

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
from app.base.models import User, Portfolio

from app.base.util import verify_pass

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
        if 'msg' in session.keys():
            message = session['msg']
            session.pop('msg')    
            return render_template( 'login/login.html',
                                    form=login_form, msg=message)
        else:
            return render_template( 'login/login.html',
                                    form=login_form)

    return redirect(url_for('home_blueprint.index'))

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

@blueprint.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    #do reset stuff here!
    login_form = LoginForm(request.form)
    
    if 'next' in request.form:
        #Check if email even exisits, if it does generate a code, save code in session, then email the code out, and return template
        #If email doesn't exist, no need to save any code, just render the page 
        session['code'] = '12345'
        session['user'] = request.form['username']
        return render_template( 'login/forgotpass.html',msg=request.form['username'], errM="Bad code, or Email")
    elif 'reset' in request.form:
        #DO CHECKING FOR CODE HERE
        #IF CORRECT THEN RESET THE PASS
        #Redirect to loginpage
        #return session['code'] + ' '+ session['user']
        session['msg'] = 'Use this password: TEMPPASS115435 and please change your password once you login'
        return redirect(url_for('base_blueprint.route_default'))
    else:
        return render_template( 'login/forgotpass.html')
    

@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('base_blueprint.login'))

@blueprint.route('/shutdown')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'

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
