from app import db, celery
from app.base.models import *
from app.base.util import verify_pass, hash_pass
from flask_login import current_user
from flask import g
from jinja2 import Template
from app.home.emailsend import send_newuser__mail
import json
import datetime
import string, random
import os
import re
from functools import wraps
from decimal import Decimal
from celery.result import AsyncResult
from datetime import timedelta


def getNotifications(f):
    #DO DB STUFF TO COLLECT NOTIFICATINOS FOR CURRENT USER.
    @wraps(f)
    def decorated(*args, **kwargs):
        noti = dict()
        deposit = 0
        withdrawls = 0

        if current_user.role == 'admin':
            alerts = notification.query.filter_by(to='admin').all()
            for alert in alerts:
                if alert.service == 'deposit':
                    deposit += 1
                elif alert.service == 'withdrawl':
                    withdrawls += 1
                else:
                    pass
            
            if deposit != 0:
                noti['deposit'] = 'You have ' + str(deposit) + ' active deposit request(s)'
            
            if withdrawls != 0:
                noti['withdrawls'] = 'You have ' + str(withdrawls) + ' active withdrawl request(s)'
        else:
            alerts = notification.query.filter_by(uuid=current_user.uuid, to='user').all()
            for alert in alerts:
                if alert.service == 'deposit':
                    deposit += 1
                elif alert.service == 'withdrawl':
                    withdrawls += 1
                else:
                    pass
            
            if deposit != 0:
                noti['deposit'] = 'There is ' + str(deposit) + ' update to your deposit request(s)'
            
            if withdrawls != 0:
                noti['withdrawls'] = 'There is ' + str(withdrawls) + ' update to your withdrawl request(s)'


                

        #noti['deposit'] = "YOU HAVE 5 DEPOSITS"
        g.notifications = noti
        return f(*args, **kwargs)
    return decorated

def clear_noti():
    try:

        if current_user.role == 'admin':
            alll = notification.query.filter_by(to='admin').all()
            for noti in alll:
                noti.to = "clear"
                db.session.commit()
        else:
            uuid = current_user.uuid
            
            alll = notification.query.filter_by(uuid=uuid, to='user').all()
            for noti in alll:
                db.session.delete(noti)
                db.session.commit()

            # alll = notification.query.filter_by(uuid=uuid).all()
            # for noti in alll:
            #     noti.to = "clear"
            #     db.session.commit()


    except:
        pass


def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

@celery.task(name='task.invested_rebalance')
def portfolio_rebalance():
    try:
        parteners = Portfolio.query.all()

        #Make sure user with ID 1 is the total and weight 1.
        for partner in parteners:
            if partner.id == 1:
                master = partner
                master.invested = 0
                #master.weight = 1.0

        for partner in parteners:
            if partner.id != 1:
                master.invested = master.invested + partner.invested

        db.session.commit()
        total_rebalance.delay()
    except:
        pass

@celery.task(name='task.total_rebalance')
def total_rebalance():
    try:
        parteners = Portfolio.query.all()
        
        for partner in parteners:
            partner.total = (partner.invested + partner.gltotal) - partner.withdrawls

        #Make sure user with ID 1 is the total and weight 1.
        for partner in parteners:
            if partner.id == 1:
                master = partner
                master.total = 0
                master.weight = 1.0

        for partner in parteners:
            if partner.id != 1:
                master.total = master.total + partner.total

        for partner in parteners:
            if partner.id != 1:
                partner.weight = partner.total / master.total

        db.session.commit() 
    except:
        pass

def profile_save(content):

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
            port.name = content['name']
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
            tempPass = get_random_string(8)
            pwd = hash_pass( tempPass )
            userNew.password = pwd
            userNew.created_at = datetime.datetime.now().date()
            
            portNew = Portfolio()
            portNew.email = content['email']
            portNew.name = content['name']
            portNew.invested = 0
            portNew.weight = 0
            portNew.gains = 0
            portNew.gltotal = 0
            portNew.losses = 0
            portNew.withdrawls = 0
            portNew.total = 0

            db.session.add(userNew)
            db.session.add(portNew)
            db.session.commit()

            try:
                base_dir = os.getcwd() + '/app/home/templates'
                tes = os.path.join(base_dir,'newuser.html')
                htmll = Template(open(tes).read()).render(username=userNew.username, password=tempPass, name=userNew.name)       
                send_newuser__mail.delay(userNew.email,htmll)
            except Exception as ex:
                print(ex)

        #Add the user or update the user then send 200, 
        #return json.dumps({'save':'failed'}), 404, {'ContentType':'application/json'}
        return json.dumps({'save':'success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'save':'failed'}), 400, {'ContentType':'application/json'}

def profile_delete(content):
    try:
        if content['id'] == '1':
            return json.dumps({'save':'failed'}), 404, {'ContentType':'application/json'}
        else:
            
            count = User.query.filter_by(id=content['id']).count()
            if count != 0:
                user = User.query.filter_by(id=content['id']).one()
                port = Portfolio.query.filter_by(email=user.email).one()

                uG = UserGraveyard()
                uG.username = user.username
                uG.email = user.email
                uG.full_name = user.name
                uG.uuid = user.uuid
                uG.deleted_at = datetime.datetime.now().date()
                uG.password = user.password
                uG.role = user.role

                db.session.add(uG)

                db.session.delete(user)
                db.session.delete(port)
                db.session.commit()
                return json.dumps({'save':'success'}), 200, {'ContentType':'application/json'}
            else:
                return json.dumps({'save':'success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'save':'failed'}), 400, {'ContentType':'application/json'}

#NEW Deposit request is POST with just 1 param of a number. Else It will be and edit and you need all info
def deposit_request(content):
    try:
        user = User.query.filter_by(username=current_user.username).first()
        
        try:
            amnt = content['deposit amount']
            changeAmonut = re.sub("[^\d\.]", "", amnt)
            status = content['status']
            date = content['date']

            if status != 'Pending':
                return json.dumps({'Deposit Edit':'Failed'}), 400, {'ContentType':'application/json'}

        
            #COULD BE PERFORMACE ISSUES DOWN THE LINE :)
            depo_req = Deposit.query.filter_by(uuid=user.uuid, date=date, status='Pending').first()
            
            if depo_req:
                
                depo_req.amount = changeAmonut
                db.session.commit()
                 
            else:
                return json.dumps({'Deposit Edit':'Failed'}), 400, {'ContentType':'application/json'}

            
            return json.dumps({'Deposit Edit':'success'}), 200, {'ContentType':'application/json'}

        except:
            #THIS WILL BE FOR NEW REQUESTS, DEPOSIT TAKES JUST The First ARGUMENT, Can submit once every week
            depo_req = Deposit.query.filter_by(uuid=user.uuid, status='Pending').all()
            depo_req = sorted(depo_req, key=lambda o: o.date)
            if depo_req:
                today = datetime.date.today()
                lastreq = depo_req[-1].date
                diff = today - lastreq
                if diff.days < 6:
                    return json.dumps({'Deposit Request':'Failed'}), 400, {'ContentType':'application/json'}
                
            for item in content:
                amount = re.sub("[^\d\.]", "", content[item])
                break

            new_deposit = Deposit()
            new_deposit.amount = amount
            new_deposit.status = 'Pending'
            new_deposit.date = datetime.datetime.now().date()
            new_deposit.uuid = user.uuid
            
            db.session.add(new_deposit)

            noti = notification()
            noti.uuid = user.uuid
            noti.to = 'admin'
            noti.service = 'deposit'
            db.session.add(noti)

            db.session.commit()

            return json.dumps({'Deposit Request':'success'}), 200, {'ContentType':'application/json'}

         
        return json.dumps({'Deposit Request':'Server Error'}), 500, {'ContentType':'application/json'}

    except:
        return json.dumps({'Deposit Request':'failed'}), 400, {'ContentType':'application/json'}

#Delete any current open requests
def deposit_request_delete(content):
    try:
        #print(content)
        if content['status'] != 'Pending':
            return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}
        
        date = content['date']
        #amount = content['deposit amount'] Possibly use amount also for search to get 

        del_req = Deposit.query.filter_by(uuid=current_user.uuid, date=date, status='Pending').first()

        if del_req:
            if del_req.status != 'Pending':
                return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}
            
            db.session.delete(del_req)
            noti = notification.query.filter_by(uuid=del_req.uuid).first()
            db.session.delete(noti)
            db.session.commit()

        else:
            return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}


       
        return json.dumps({'Deposit Delete':'success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}

def deposit_request_admin_approve(content):
    try:
        
        date = content['date']
        user = content['user id']
        first_user = User.query.filter_by(id=1).first()
        #amount = content['deposit amount'] Possibly use amount also for search to get 

        del_req = Deposit.query.filter_by(uuid=user, date=date, status='Pending').first()

        if del_req:
            
            #TO DO ADD THE AMOUNT SENT IN, TO PORTFOLIO AND THEN MARK AS APPROVED
            if del_req.uuid != first_user.uuid:
                acc = User.query.filter_by(uuid=del_req.uuid).first()
                port = Portfolio.query.filter_by(email=acc.email).first()

                port.invested += del_req.amount

            del_req.status = "Approved"
            del_req.dateApproved = datetime.datetime.now().date()

            noti = notification.query.filter_by(uuid=del_req.uuid).first()
            noti.to = 'user'
        
            #DO THE BELOW INCASE ADMIN CHANGES IT MANUALLY, BUT MUST CLEAR THE $xxxxx
            # if content['deposit amount'] != del_req.amount:
            #     del_req.amount = content['deposit amount']
            
            db.session.commit()
            portfolio_rebalance.delay()

        else:
            return json.dumps({'DB Error':'failed'}), 400, {'ContentType':'application/json'}


       
        return json.dumps({'Deposit Approved':'success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'Request Format Bad':'failed'}), 400, {'ContentType':'application/json'}

def deposit_request_admin_deny(content):
    try:
        
        date = content['date']
        user = content['user id']
        #amount = content['deposit amount'] Possibly use amount also for search to get 

        del_req = Deposit.query.filter_by(uuid=user, date=date, status='Pending').first()

        if del_req:
            if del_req.status != 'Pending':
                return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}

            del_req.status = "Denied"
            del_req.dateApproved = datetime.datetime.now().date()

            noti = notification.query.filter_by(uuid=del_req.uuid).first()
            noti.to = 'user'
           
            #DO THE BELOW INCASE ADMIN CHANGES IT MANUALLY, BUT MUST CLEAR THE $xxxxx
            # if content['deposit amount'] != del_req.amount:
            #     del_req.amount = content['deposit amount']
            
            db.session.commit()
            

        else:
            return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}


       
        return json.dumps({'Deposit Delete':'success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'Request Format Bad':'failed'}), 400, {'ContentType':'application/json'}

def partners_edit(content):
    #print(content)
    try:
        port = Portfolio.query.filter_by(email=content['email']).first()

        if port:
            if port.id != 1:
                port.invested = re.sub("[^\d\.]", "", content['deposited'])
                db.session.commit()
                #portfolio_rebalance()
        else:
            return json.dumps({'DB Error':'failed'}), 400, {'ContentType':'application/json'}

        return json.dumps({'Partner Edit':'success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'Request Format Bad':'failed'}), 400, {'ContentType':'application/json'}

@celery.task(name='task.update_gain_loss_partners')
def update_gain_loss_partners(dGLO, updateOnly): #THIS IS UPDATING THE GAIN_LOSS TABLE -> PARTNERS, DAILY_GAIN_LOSS -> ADMIN 1 ENTRY DAILY
    try:
        
        if updateOnly:
            #print("DAY EXISITS THAT MEANS YOU MUST LOOP AND UPDATE")
            entries = Gain_Loss.query.filter_by(date=dGLO).all()
            data = Daily_Gain_Loss.query.filter_by(date=dGLO).first()
            for entry in entries:
                user = User.query.filter_by(uuid=entry.uuid).first()
                port = Portfolio.query.filter_by(email=user.email).first()

                if data.gainType == 'gain' and entry.gainType == 'gain':
                    port.gains = port.gains - entry.amount
                    port.gltotal = port.gltotal - entry.amount

                    entry.amount = (data.amount * entry.calcWeight)

                    port.gains = port.gains + (data.amount * entry.calcWeight)
                    port.gltotal = port.gltotal + (data.amount * entry.calcWeight)
                
                elif data.gainType == 'loss' and entry.gainType == 'loss':
                    port.losses = port.losses - entry.amount
                    port.gltotal = port.gltotal + entry.amount

                    entry.amount = (data.amount * entry.calcWeight)

                    port.losses = port.losses + (data.amount * entry.calcWeight)
                    port.gltotal = port.gltotal - (data.amount * entry.calcWeight)
                
                elif data.gainType == 'gain' and entry.gainType == 'loss':
                    port.losses = port.losses - entry.amount
                    port.gltotal = port.gltotal + entry.amount

                    entry.amount = (data.amount * entry.calcWeight)

                    port.gains = port.gains + (data.amount * entry.calcWeight)
                    port.gltotal = port.gltotal + (data.amount * entry.calcWeight)

                else:#data.gainType == 'loss' and entry.gainType == 'gain'
                    port.gains = port.gains - entry.amount
                    port.gltotal = port.gltotal - entry.amount

                    entry.amount = (data.amount * entry.calcWeight)

                    port.losses = port.losses + (data.amount * entry.calcWeight)
                    port.gltotal = port.gltotal - (data.amount * entry.calcWeight)

                entry.gainType = data.gainType
                db.session.commit()
        else:
            #print("So new entries for this date")
            users = User.query.all()
            data = Daily_Gain_Loss.query.filter_by(date=dGLO).first()
            for user in users:
                nGL = Gain_Loss()
                port = Portfolio.query.filter_by(email=user.email).first()
                nGL.uuid = user.uuid
                nGL.date = data.date

                if data.gainType == 'gain':
                    nGL.amount = (data.amount * port.weight)

                    port.gains = port.gains + nGL.amount
                    port.gltotal = port.gltotal + nGL.amount
                else:
                    nGL.amount = (data.amount * port.weight)

                    port.losses = port.losses + nGL.amount
                    port.gltotal = port.gltotal - nGL.amount

                nGL.calcWeight = port.weight
                nGL.gainType = data.gainType
                db.session.add(nGL)
                db.session.commit()

        total_rebalance.delay()
        return True

    except Exception as e:
        pass
        #print(e)

def gains_losses(content):
    try:

        entry = Daily_Gain_Loss.query.filter_by(date=content['date']).first()

        if entry:
            #TO DO RESTRICT EDIT AFTER A NEW DATE HAS BEEN PUT IN BECAUSE OF COMPOUND WEIGHTS RECALC TOO MUCH WORK
 
            entry.amount = re.sub("[^\d\.]", "", content['amount'])
            
            if content['gain or loss'].lower() != 'gain' and content['gain or loss'].lower() != 'loss':
                entry.gainType = 'gain'
            else:
                entry.gainType = content['gain or loss'].lower()
            
            db.session.commit()
            update_gain_loss_partners.delay(content['date'],True)

        else:
            try:
                newdgl = Daily_Gain_Loss()
                newdgl.date = content['date']
                newdgl.amount = re.sub("[^\d\.]", "", content['amount'])

                if content['gain or loss'].lower() != 'gain' and content['gain or loss'].lower() != 'loss':
                    newdgl.gainType = 'gain'
                else:
                    newdgl.gainType = content['gain or loss'].lower()

                db.session.add(newdgl)
                db.session.commit()
                update_gain_loss_partners.delay(content['date'],False)
            except:
                return json.dumps({'DB Error':'failed'}), 500, {'ContentType':'application/json'}

        return json.dumps({'Gain/Loss Update':'success'}), 200, {'ContentType':'application/json'}
    
    except:
        return json.dumps({'Request Format Bad':'failed'}), 400, {'ContentType':'application/json'}


def withdrawl_request(content):
    try:
        user = User.query.filter_by(username=current_user.username).first()
        
        #WILL HAVE TO DO THE CHECKS IN EACH TRY EXCEPT
        #amnt = content['withdrawl amount']
        #DO CHECK TO MAKE SURE THEY CAN EVEN WITHDRAW THIS MUCH
        
        try:
            amnt = content['withdrawl amount']
            changeAmonut = re.sub("[^\d\.]", "", amnt)
            status = content['status']
            date = content['date']
            
            port = Portfolio.query.filter_by(email=user.email).first()
            if (port.total - Decimal(changeAmonut)) < 0:
                return json.dumps({'Withdrawl Edit':'Failed'}), 400, {'ContentType':'application/json'}

            if status != 'Pending':
                return json.dumps({'Withdrawl Edit':'Failed'}), 400, {'ContentType':'application/json'}

            with_req = Withdrawl.query.filter_by(uuid=user.uuid, date=date, status='Pending').first()
            
            if with_req:
                
                with_req.amount = changeAmonut

                taxAndfee = taxes_fees.query.first()
                tax = taxAndfee.taxes
                fee = taxAndfee.fees

                changeAmonut = Decimal(changeAmonut)
                with_req.taxes = changeAmonut * tax
                with_req.fees = changeAmonut * fee
                with_req.paidout = changeAmonut - with_req.taxes - with_req.fees

                db.session.commit()

            else:
                return json.dumps({'Withdraw Edit':'Failed'}), 400, {'ContentType':'application/json'}

            
            return json.dumps({'Withdraw Edit':'success'}), 200, {'ContentType':'application/json'}

        except:
            #THIS WILL BE FOR NEW REQUESTS, DEPOSIT TAKES JUST The First ARGUMENT, Can submit once every week
            
            with_req = Withdrawl.query.filter_by(uuid=user.uuid, status='Pending').all()
            with_req = sorted(with_req, key=lambda o: o.date)
            if with_req:
                today = datetime.date.today()
                lastreq = with_req[-1].date
                diff = today - lastreq
                if diff.days < 6:
                    return json.dumps({'Withdrawl Request':'Failed Need To wait 6 days from last one'}), 400, {'ContentType':'application/json'}
                
            for item in content:
                amount = re.sub("[^\d\.]", "", content[item])
                break
            
            port = Portfolio.query.filter_by(email=user.email).first()
            if (port.total - Decimal(amount)) < 0:
                return json.dumps({'Withdrawl Edit':'Failed'}), 400, {'ContentType':'application/json'}
      
            new_withdrawl = Withdrawl()
            new_withdrawl.uuid = user.uuid
            new_withdrawl.amount = amount
            new_withdrawl.status = 'Pending'
            new_withdrawl.date = datetime.datetime.now().date()

            taxAndfee = taxes_fees.query.first()
            tax = taxAndfee.taxes
            fee = taxAndfee.fees
            amount = Decimal(amount)
            new_withdrawl.taxes = amount * tax
            new_withdrawl.fees = amount * fee
            new_withdrawl.paidout = amount - new_withdrawl.taxes - new_withdrawl.fees
        
            db.session.add(new_withdrawl)

            noti = notification()
            noti.uuid = user.uuid
            noti.to = 'admin'
            noti.service = 'withdrawl'
            db.session.add(noti)

            db.session.commit()
           

            return json.dumps({'Withdrawl Request':'success'}), 200, {'ContentType':'application/json'}

         
        return json.dumps({'Withdrawl Request':'Server Error'}), 500, {'ContentType':'application/json'}

    except:
        return json.dumps({'Withdrawl Request':'failed'}), 400, {'ContentType':'application/json'}

#Delete any current open requests
def withdrawl_request_delete(content):
    try:
        #print(content)
        if content['status'] != 'Pending':
            return json.dumps({'Withdraw Delete':'failed'}), 400, {'ContentType':'application/json'}
        
        date = content['date']
        #amount = content['deposit amount'] Possibly use amount also for search to get 

        with_req = Withdrawl.query.filter_by(uuid=current_user.uuid, date=date, status='Pending').first()

        if with_req:
            if with_req.status != 'Pending':
                return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}
            
            db.session.delete(with_req)
            noti = notification.query.filter_by(uuid=with_req.uuid).first()
            db.session.delete(noti)
            db.session.commit()
        else:
            return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}

        return json.dumps({'Deposit Delete':'success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}

def withdrawl_request_admin_approve(content):
    try:
        
        date = content['date']
        user = content['user id']
        first_user = User.query.filter_by(id=1).first()
        #amount = content['deposit amount'] Possibly use amount also for search to get 

        with_req = Withdrawl.query.filter_by(uuid=user, date=date, status='Pending').first()
        
        if with_req:
            
            #TO DO ADD THE AMOUNT SENT IN, TO PORTFOLIO AND THEN MARK AS APPROVED
            if with_req.uuid != first_user.uuid:
                acc = User.query.filter_by(uuid=with_req.uuid).first()
                port = Portfolio.query.filter_by(email=acc.email).first()

                port.withdrawls += with_req.amount

                portt = Portfolio.query.filter_by(id=1).first()
                portt.withdrawls += with_req.amount


            with_req.status = "Approved"
            with_req.dateApproved = datetime.datetime.now().date()

            noti = notification.query.filter_by(uuid=with_req.uuid).first()
            noti.to = 'user'

            #DO THE BELOW INCASE ADMIN CHANGES IT MANUALLY, BUT MUST CLEAR THE $xxxxx
            # if content['deposit amount'] != del_req.amount:
            #     del_req.amount = content['deposit amount']
            
            db.session.commit()
            total_rebalance.delay()

        else:
            return json.dumps({'DB Error':'failed'}), 400, {'ContentType':'application/json'}


       
        return json.dumps({'Deposit Approved':'success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'Request Format Bad':'failed'}), 400, {'ContentType':'application/json'}

def withdrawl_request_admin_deny(content):
    try:
        
        date = content['date']
        user = content['user id']
        #amount = content['deposit amount'] Possibly use amount also for search to get 

        del_req = Withdrawl.query.filter_by(uuid=user, date=date, status='Pending').first()

        if del_req:
            if del_req.status != 'Pending':
                return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}

            del_req.status = "Denied"
            del_req.dateApproved = datetime.datetime.now().date()

            noti = notification.query.filter_by(uuid=with_req.uuid).first()
            noti.to = 'user'

            #DO THE BELOW INCASE ADMIN CHANGES IT MANUALLY, BUT MUST CLEAR THE $xxxxx
            # if content['deposit amount'] != del_req.amount:
            #     del_req.amount = content['deposit amount']
            
            db.session.commit()
            

        else:
            return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}


       
        return json.dumps({'Deposit Delete':'success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'Request Format Bad':'failed'}), 400, {'ContentType':'application/json'}

def update_tax_fee(content):

    try:
        taxAndfee = taxes_fees.query.first()

        if taxAndfee:
            pass
        else:
            tf = taxes_fees()
            tf.taxes = 0
            tf.fees = 0
            db.session.add(tf)
            db.session.commit()

        if 'tax' in content.keys():
            tax = re.sub("[^\d\.]", "", content['tax'])
            tax = float(tax) / 100

            taxAndfee.taxes = tax
            db.session.commit()
            return json.dumps({'Tax Update':'Success'}), 200, {'ContentType':'application/json'}  
        else:
            fee = re.sub("[^\d\.]", "", content['fee'])
            fee = float(fee) / 100

            taxAndfee.fees = fee
            db.session.commit()
            return json.dumps({'Fee Update':'Success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'Update':'failed'}), 400, {'ContentType':'application/json'}
        pass

@celery.task(name='task.health_check')
def workerHealthCheck():
    try:
        x = 1
        y = 2
        z = x + y
        return z
    except:
        pass

def healthCheck():
    try:
        hc = celery_health().query.first()
        
        if hc:
            if hc.status == 'PENDING':
                res = celery.AsyncResult(hc.taskID)
                if res.status == 'SUCCESS':
                    hc.status = res.status
                    db.session.commit()
                return False
            else:
                db.session.delete(hc)
                db.session.commit()
                return True

        task = workerHealthCheck.delay()
        hc = celery_health()
        hc.taskID = task.id
        hc.status = task.status
        db.session.add(hc)
        db.session.commit()
    except Exception as e:
        pass

def chartUpdate():
    try:
        day = datetime.datetime.today().strftime('%A')
        if day == 'Monday':
            filterr = datetime.datetime.now().date()
            gainAndLoss = db.session.query(Gain_Loss).filter(Gain_Loss.date <= filterr, (Gain_Loss.date-filterr) > -1).filter_by(uuid=current_user.uuid).all()
        elif day == 'Tuesday':
            filterr = datetime.datetime.now().date()
            gainAndLoss = db.session.query(Gain_Loss).filter(Gain_Loss.date <= filterr, (Gain_Loss.date-filterr) > -2).filter_by(uuid=current_user.uuid).all()
        elif day == 'Wednesday':
            filterr = datetime.datetime.now().date()
            gainAndLoss = db.session.query(Gain_Loss).filter(Gain_Loss.date <= filterr, (Gain_Loss.date-filterr) > -3).filter_by(uuid=current_user.uuid).all()
        elif day == 'Thursday':
            filterr = datetime.datetime.now().date()
            gainAndLoss = db.session.query(Gain_Loss).filter(Gain_Loss.date <= filterr, (Gain_Loss.date-filterr) > -4).filter_by(uuid=current_user.uuid).all()
        elif day == 'Friday':
            filterr = datetime.datetime.now().date()
            gainAndLoss = db.session.query(Gain_Loss).filter(Gain_Loss.date <= filterr, (Gain_Loss.date-filterr) > -5).filter_by(uuid=current_user.uuid).all()
        else:
            filterr = datetime.datetime.now().date()
            gainAndLoss = db.session.query(Gain_Loss).filter(Gain_Loss.date <= filterr, (Gain_Loss.date-filterr) > -7).filter_by(uuid=current_user.uuid).all()

        dat = []
        gainAndLoss = sorted(gainAndLoss, key=lambda o: o.date)
        for i in gainAndLoss:
            if i.gainType == 'gain':
                dat.append(float(i.amount))
            else:
                dat.append(float(-i.amount))

        gainAndL = Gain_Loss.query.filter_by(uuid=current_user.uuid).all()
        datM = [0] * 12
        for entry in gainAndL:
            date = entry.date
            if entry.gainType == 'gain':
                datM[date.month - 1] += float(entry.amount)
            else:
                datM[date.month - 1] -= float(entry.amount)

        return json.dumps({'daily':dat,'monthly':datM}), 200, {'ContentType':'application/json'}
    except Exception as e:
        print(e)
        dat = []
        datM = []
        return json.dumps({'daily':dat,'monthly':datM}), 400, {'ContentType':'application/json'}
