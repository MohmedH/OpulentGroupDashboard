# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from app.home import blueprint
from app.base.util import verify_pass, hash_pass
from app.base.models import User, Portfolio
from app.base.forms import ChangePassword, UpdateProfile
from flask import render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app import login_manager, db
from jinja2 import TemplateNotFound

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


#If you ever update email, that is the pm key that connects all the other tables, so you must update that accordingly
@blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def page_user():
    if not current_user.is_authenticated:
        return redirect(url_for('base_blueprint.login'))

    #Use the bottom after a sussessful password reset or any message for that matter
    #return render_template('profile.html', passmsg="Success")
    pass_form = ChangePassword(request.form)
    profile_form = UpdateProfile(request.form)
    
    #If the username is not unique this falls apart as anyone can change username to match and then change that password.
    if 'changePass' in request.form:
        user = User.query.filter_by(username=current_user.username).first()
        passwordOld = request.form['passwordOld']
        passwordNew = request.form['passwordNew']
        passwordVerify = request.form['passwordVerify']
        if user and verify_pass( passwordOld, user.password):
            if passwordNew == passwordVerify:
                #Change the password here!
                pwd = hash_pass( passwordNew )
                user.password = pwd
                db.session.commit()
                passmsgg = 'Successfully Changed Password!'
            else:
                passmsgg = 'error New passwords did not match!'
        else:
            passmsgg = 'error please make sure you entered the current password properly'

        return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, passmsg=passmsgg)
    #This is for updating information to the profile, **!!IF EMAIL CHANGES YOU MUST CHANGE IN ALL TABLES!!**
    elif 'updateProfile' in request.form:
        print(request.form)
        username  = request.form['username']
        email     = request.form['email'   ]
        
        #First Check make sure the user name in the form is different from current, meaning they want to change it
        if username != current_user.username:
            #Now Query that user and make sure that it does not already exist
            user = User.query.filter_by(username=username).first()
            if user:
                return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, profilemsg='Error User already exists')
            else:
                #If you get here you will be able to change that username, because it does not exist, and it is not the same as current
                changeUser = True
        else:
            changeUser = False


        if email != current_user.email:   
            user = User.query.filter_by(email=email).first()
            if user:
                return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, profilemsg='Error Email already exists')
            else:
                changeEmail = True
        else:
            changeEmail = False

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
    
        if changeEmail or changeUser:
            #Commit the changes!
            db.session.commit()
            return render_template('profile.html', formpassword=pass_form, formprofile=profile_form, profilemsg='Changed Info Successfully!')
        else:
            return render_template('profile.html', formpassword=pass_form, formprofile=profile_form)
    else:
        #Default page render, just want to see what's going on
        return render_template('profile.html', formpassword=pass_form, formprofile=profile_form)


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
