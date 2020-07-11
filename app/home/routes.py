# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from app.base.util import verify_pass, hash_pass
from app.base.models import User, Portfolio
from app.base.forms import ChangePassword, UpdateProfile
from flask import render_template, redirect, url_for, request, jsonify, Response, Flask
from flask_login import login_required, current_user
from app import login_manager, db
from jinja2 import TemplateNotFound
import json

@blueprint.route('/index')
@login_required
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

@blueprint.route('/withdraw', methods=['GET','POST'])
@login_required
def with_draw():
   
    if request.method == 'POST':
        print(request.get_json())
        return json.dumps({'save':'failed'}), 404, {'ContentType':'application/json'}
        #return json.dumps({'save':'success'}), 200, {'ContentType':'application/json'}

    #Normal Get Reqs, Going to have to send a list of all current requests with this rendertemplate, and also a few completed requests
    return render_template('withdraw.html')

@blueprint.route('/partners', methods=['GET'])
@login_required
def partners():
    try:
        if  current_user.role != 'admin':
            return render_template('page-403.html'), 403
        else:
            users = Portfolio.query.all()
            return render_template('partners.html', partner=users)
    except:
        return render_template('page-500.html'), 500


@blueprint.route('/profiles', methods=['GET'])
@login_required
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
def profileActions(action):
    if  current_user.role != 'admin':
        return json.dumps({'save':'failed'}), 401, {'ContentType':'application/json'}
    
    if action != 'save':
        return json.dumps({'Error':'Not Found'}), 404, {'ContentType':'application/json'}

    if request.method == 'POST' or request.method == 'PUT':
        content = request.get_json()
        #print(content)

        try:
            user = User.query.filter_by(id=content['id']).first()

            if user:
                if User.query.filter_by(username=content['username']).first() and user.username != content['username']:
                    return json.dumps({'save':'failed'}), 401, {'ContentType':'application/json'}

                if User.query.filter_by(username=content['email']).first() and user.email != content['email']:
                    return json.dumps({'save':'failed'}), 401, {'ContentType':'application/json'}

                port = Portfolio.query.filter_by(email=user.email).first()
                user.username = content['username']
                user.email = content['email']
                user.name = content['name']
                port.email = content['email']
                db.session.commit()


            else:
                userEmailCheck = User.query.filter_by(email=content['email']).first()
                if userEmailCheck:
                    return json.dumps({'save':'failed'}), 404, {'ContentType':'application/json'}

                userNameCheck = User.query.filter_by(username=content['username']).first()
                if userNameCheck:
                    return json.dumps({'save':'failed'}), 404, {'ContentType':'application/json'}

                userNew = User()
                userNew.username = content['username']
                userNew.email = content['email']
                userNew.name = content['name']
                pwd = hash_pass( 'pass' )
                userNew.password = pwd

                portNew = Portfolio()
                portNew.email = content['email']
                portNew.invested = 0

                db.session.add(userNew)
                db.session.add(portNew)
                db.session.commit()

            #Add the user or update the user then send 200, 
            #return json.dumps({'save':'failed'}), 404, {'ContentType':'application/json'}
            return json.dumps({'save':'success'}), 200, {'ContentType':'application/json'}
        except:
            return json.dumps({'save':'failed'}), 400, {'ContentType':'application/json'}
    
    if request.method == 'DELETE':
        try:
            content = request.get_json()
            #print(content)
            if content['id'] == '1':
                return json.dumps({'save':'failed'}), 404, {'ContentType':'application/json'}
            else:
                
                count = User.query.filter_by(id=content['id']).count()
                if count != 0:
                    user = User.query.filter_by(id=content['id']).one()
                    port = Portfolio.query.filter_by(email=user.email).one()
                    db.session.delete(user)
                    db.session.delete(port)
                    db.session.commit()
                    return json.dumps({'save':'success'}), 200, {'ContentType':'application/json'}
                else:
                    return json.dumps({'save':'success'}), 200, {'ContentType':'application/json'}
            

        except:
            return json.dumps({'save':'failed'}), 400, {'ContentType':'application/json'}

#If you ever update email, that is the pm key that connects all the other tables, so you must update that accordingly
@blueprint.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
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

            #Change username in USER table
            if changeUser:
                user.username = username
            
            #Change email in USER and PORTFOLIO tables
            if changeEmail:
                portfolio = Portfolio.query.filter_by(email=current_user.email).first()
                user.email = email
                portfolio.email = email
            
            user.name = name

            db.session.commit()
            #return redirect(url_for('page_user', formpassword=pass_form, formprofile=profile_form, username=current_user.username))
            return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, profilemsg='Changed Info Successfully!')
            
            
            ''' OLD WAY
            if changeEmail or changeUser:
                #Commit the changes!
                db.session.commit()
                return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, profilemsg='Changed Info Successfully!')
            else:
                return render_template('profile.html', formpassword=pass_form, formprofile=profile_form)
            '''
        else:
            #Default page render, just want to see what's going on
            return render_template('profile.html', formpassword=pass_form, formprofile=profile_form)
    except:
        return render_template('page-500.html'), 500



@blueprint.route('/<template>')
def route_template(template):

    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    try:

        return render_template(template + '.html')

    except TemplateNotFound:
        return render_template('page-404.html'), 404
    
    except:
        return render_template('page-500.html'), 500
