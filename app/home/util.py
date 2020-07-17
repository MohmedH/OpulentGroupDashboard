from app import db
from app.base.models import User, Portfolio, Deposit, UserGraveyard
from app.base.util import verify_pass, hash_pass
from flask_login import current_user
from jinja2 import Template
from app.home.emailsend import send_newuser__mail
import json
import datetime
import string, random
import os

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

def portfolio_rebalance():
    try:
        parteners = Portfolio.query.all()

        #Make sure user with ID 1 is the total and weight 1.
        for partner in parteners:
            if partner.id == 1:
                master = partner
                master.invested = 0
                master.weight = 1.0

        for partner in parteners:
            if partner.id != 1:
                master.invested = master.invested + partner.invested

        for partner in parteners:
            if partner.id != 1:
                partner.weight = partner.invested / master.invested

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
            portNew.weight = 0.0

            db.session.add(userNew)
            db.session.add(portNew)
            db.session.commit()

            try:
                base_dir = os.getcwd() + '/app/home/templates'
                tes = os.path.join(base_dir,'newuser.html')
                htmll = Template(open(tes).read()).render(username=userNew.username, password=tempPass, name=userNew.name)       
                send_newuser__mail(userNew.email,htmll)
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
            changeAmonut = content['deposit amount']
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
            
            if depo_req:
                today = datetime.date.today()
                lastreq = depo_req[-1].date
                diff = today - lastreq
                if diff.days < 6:
                    return json.dumps({'Deposit Request':'Failed'}), 400, {'ContentType':'application/json'}
                
            for item in content:
                amount = content[item]
                break

            new_deposit = Deposit()
            new_deposit.amount = amount
            new_deposit.status = 'Pending'
            new_deposit.date = datetime.datetime.now().date()
            new_deposit.uuid = user.uuid
            
            db.session.add(new_deposit)
            db.session.commit()

            return json.dumps({'Deposit Request':'success'}), 200, {'ContentType':'application/json'}

         
        return json.dumps({'Deposit Request':'Server Error'}), 500, {'ContentType':'application/json'}

    except:
        return json.dumps({'Deposit Request':'failed'}), 400, {'ContentType':'application/json'}

#Delete any current open requests
def deposit_request_delete(content):
    try:
        print(content)
        if content['status'] != 'Pending':
            return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}
        
        date = content['date']
        #amount = content['deposit amount'] Possibly use amount also for search to get 

        del_req = Deposit.query.filter_by(uuid=current_user.uuid, date=date, status='Pending').first()

        if del_req:
            if del_req.status != 'Pending':
                return json.dumps({'Deposit Delete':'failed'}), 400, {'ContentType':'application/json'}
            
            db.session.delete(del_req)
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

            #DO THE BELOW INCASE ADMIN CHANGES IT MANUALLY, BUT MUST CLEAR THE $xxxxx
            # if content['deposit amount'] != del_req.amount:
            #     del_req.amount = content['deposit amount']
            
            db.session.commit()
            portfolio_rebalance()

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

            port.invested = content['invested']
            db.session.commit()
            #portfolio_rebalance()
        else:
            return json.dumps({'DB Error':'failed'}), 400, {'ContentType':'application/json'}

        return json.dumps({'Partner Edit':'success'}), 200, {'ContentType':'application/json'}
    except:
        return json.dumps({'Request Format Bad':'failed'}), 400, {'ContentType':'application/json'}
