# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from app.home.util import *
from app.base.util import verify_pass, hash_pass
from app.base.models import User, Portfolio, Deposit, Daily_Gain_Loss
from app.base.forms import ChangePassword, UpdateProfile
from flask import render_template, redirect, url_for, request, jsonify, Response, Flask
from flask_login import login_required, current_user
from app import login_manager, db
from jinja2 import TemplateNotFound
import json

@blueprint.route('/index')
@login_required
@getNotifications
def index():
    
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    dataPortfolio = Portfolio.query.filter_by(email=current_user.u_email()).first()

    # use this incase of NoneType Errors
    if(dataPortfolio):
        investmentAmt = dataPortfolio.invested
        investmentAmt = "{:,}".format(investmentAmt)
    else:
        investmentAmt = 'error'

        #Use the bottom to update rows
        #data.invested = 50
        #db.session.commit()
    dataDailySalesChart = {}
    dataDailySalesChart["labels"] = ['M', 'T', 'W', 'TH', 'F']
    dataDailySalesChart["series"] = [900, 500, 400, -120, 500]

    return render_template('index.html', chart = dataDailySalesChart, investAMT=investmentAmt)

@blueprint.route('/disclosure')
@login_required
@getNotifications
def page_disclosure():
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    return render_template('disclosure.html')


#If you ever update email, that is the pm key that connects all the other tables, so you must update that accordingly
@blueprint.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
@getNotifications
def page_user(username):
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    if username != current_user.username:
        return render_template('page-403.html'), 403

    try:
        #Use the bottom after a sussessful password reset or any message for that matter
        #return render_template('profile.html', passmsg="Success")
        pass_form = ChangePassword(request.form)
        profile_form = UpdateProfile(request.form)
        
        #If the username is not unique this falls apart as anyone can change username to match and then change that password.
        if 'changePass' in request.form:
            print(request.form)
            user = User.query.filter_by(username=current_user.username).first()
            passwordOld = request.form['passwordOld']
            passwordNew = request.form['passwordNew']
            passwordVerify = request.form['passwordVerify']
            if user and verify_pass( passwordOld, user.password):
                if passwordNew == passwordVerify and len(passwordNew) > 5:
                    #Change the password here!
                    pwd = hash_pass( passwordNew )
                    user.password = pwd
                    db.session.commit()
                    passmsgg = 'Successfully Changed Password!'
                else:
                    passmsgg = 'error please make sure passwords match, and are 6 characters atleast'
            else:
                passmsgg = 'error please make sure you entered the current password properly'

            return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, passmsg=passmsgg)
        #This is for updating information to the profile, **!!IF EMAIL CHANGES YOU MUST CHANGE IN ALL TABLES!!**
        elif 'updateProfile' in request.form:
            #print(request.form)
            username  = request.form['username']
            email     = request.form['email'   ]
            name      = request.form['name'    ]
            
            #First Check make sure the user name in the form is different from current, meaning they want to change it
            if username != current_user.username and len(username) > 3:
                #Now Query that user and make sure that it does not already exist
                user = User.query.filter_by(username=username).first()
                if user:
                    return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, profilemsg='Error User already exists')
                else:
                    #If you get here you will be able to change that username, because it does not exist, and it is not the same as current
                    changeUser = True
            else:
                changeUser = False

            if email != current_user.email and len(email) > 3:   
                user = User.query.filter_by(email=email).first()
                if user:
                    return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, profilemsg='Error Email already exists')
                else:
                    changeEmail = True
            else:
                changeEmail = False

            if len(name) < 2:
                return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, profilemsg='Error Name must be atleast 2 characters')

            #UPDATE THE INFO HERE
            user = User.query.filter_by(username=current_user.username).first()
            portfolio = Portfolio.query.filter_by(email=current_user.email).first()

            #Change username in USER table
            if changeUser:
                user.username = username
            
            #Change email in USER and PORTFOLIO tables
            if changeEmail:
                user.email = email
                portfolio.email = email
            
            user.name = name
            portfolio.name = name

            db.session.commit()
            #return redirect('/profile/'+user.username, formpassword=pass_form, formprofile=profile_form, profilemsg='Changed Info Successfully!')
            return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, profilemsg='Changed Info Successfully!')

        else:
            #Default page render, just want to see what's going on
            return render_template('profile.html', formpassword=pass_form, formprofile=profile_form)
    except:
        return render_template('page-500.html'), 500

@blueprint.route('/withdraw', methods=['GET','POST','DELETE'])
@login_required
@getNotifications
def with_draw():
    try:
   
        if request.method == 'POST':
            print(request.get_json())
            return json.dumps({'save':'failed'}), 404, {'ContentType':'application/json'}
            #return json.dumps({'save':'success'}), 200, {'ContentType':'application/json'}

        #Normal Get Reqs, Going to have to send a list of all current requests with this rendertemplate, and also a few completed requests
        return render_template('withdraw.html')
    
    except:
        return render_template('page-500.html'), 500

#REGULAR DEPOSIT
@blueprint.route('/deposit', methods=['GET','POST','DELETE'])
@login_required
@getNotifications
def deposit():
    try:
        #NEW DEPOSIT REQUEST OR EDIT REQUEST
        if request.method == 'POST':
            return deposit_request(request.get_json())

        if request.method == 'DELETE':
            return deposit_request_delete(request.get_json())

        #Normal Get Reqs, Going to have to send a list of all current requests with this rendertemplate, and also a few completed requests
        pending = Deposit.query.filter_by(uuid=current_user.uuid, status='Pending').all()
        pending = sorted(pending, key=lambda o: o.date)
        history = Deposit.query.filter_by(uuid=current_user.uuid, status='Approved').all()
        denied = Deposit.query.filter_by(uuid=current_user.uuid, status='Denied').all()
        history = history+denied
        return render_template('deposits.html', pending=pending, history=history )
    
    except:
        return render_template('page-500.html'), 500

#######################
'''
BELOW ARE ADMIN ENDPOINTS

USE THIS TO START EACH:
if  current_user.role != 'admin':
            return render_template('page-403.html'), 403

'''
#######################

#ADMIN FOR DEPOSIT
@blueprint.route('/partners/deposit/requests', methods=['GET','POST','DELETE'])
@login_required
@getNotifications
def partners_deposits():
    try:
        if  current_user.role != 'admin':
            return render_template('page-403.html'), 403

        if request.method == 'POST':
            return deposit_request_admin_approve(request.get_json())

        if request.method == 'DELETE':
            return deposit_request_admin_deny(request.get_json())
        
        dReqs = Deposit.query.filter_by(status='Pending').all()
        history = Deposit.query.filter_by(status='Approved').all()
        history = history + Deposit.query.filter_by(status='Denied').all()
        users = User.query.all()
        return render_template('partners-deposits.html', pending=dReqs, users=users, history=history)

    except:
        return render_template('page-500.html'), 500

@blueprint.route('/partners', methods=['GET','POST'])
@login_required
@getNotifications
def partners():
    try:
        if  current_user.role != 'admin':
            return render_template('page-403.html'), 403
        else:
            if request.method == 'POST':
                #print('HERE')
                r = partners_edit(request.get_json())
                portfolio_rebalance.delay()
                return r

            partners = Portfolio.query.all()
            return render_template('partners.html', partner=partners)
    except:
        return render_template('page-500.html'), 500

@blueprint.route('/profiles', methods=['GET'])
@login_required
@getNotifications
def profile():
    try:
        if  current_user.role != 'admin':
            return render_template('page-403.html'), 403
        else:
            users = User.query.all()
            return render_template('profiles.html', test=users)
    except:
        return render_template('page-500.html'), 500

@blueprint.route('/profiles/<action>', methods=['POST', 'PUT', 'DELETE'])
@login_required
@getNotifications
def profileActions(action):
    if  current_user.role != 'admin':
        return json.dumps({'save':'failed'}), 401, {'ContentType':'application/json'}
    
    if action != 'save':
        return json.dumps({'Error':'Not Found'}), 404, {'ContentType':'application/json'}

    if request.method == 'POST' or request.method == 'PUT':     
        try:
            content = request.get_json()
            return profile_save(content)
        except:
            return json.dumps({'save':'failed'}), 400, {'ContentType':'application/json'}
   
    if request.method == 'DELETE':
        try:
            content = request.get_json()
            return profile_delete(content)
        except:
            return json.dumps({'save':'failed'}), 400, {'ContentType':'application/json'}

@blueprint.route('/update/gains_losses', methods=['GET','POST'])
@login_required
@getNotifications
def update_gains_losses():
    try:
        if  current_user.role != 'admin':
            return render_template('page-403.html'), 403
        else:
            if request.method == 'POST':
                return gains_losses(request.get_json())
        
        dailyGloss = Daily_Gain_Loss.query.all()
        return render_template('updategains.html', info=dailyGloss)

    except:
        return render_template('page-500.html'), 500


@blueprint.route('/<template>')
def route_template(template):

    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    try:
        return render_template('page-404.html'), 404
    except:
        return render_template('page-500.html'), 500
    '''
    try:

        return render_template(template + '.html')

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500
    '''
