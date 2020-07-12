from app import db
from app.base.models import User, Portfolio, Deposit
from flask_login import current_user
import json
import datetime


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
            pwd = hash_pass( 'pass' )
            userNew.password = pwd

            portNew = Portfolio()
            portNew.email = content['email']
            portNew.name = content['name']
            portNew.invested = 0

            db.session.add(userNew)
            db.session.add(portNew)
            db.session.commit()

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
            depo_req = Deposit.query.filter_by(userID=user.id, date=date).first()
            
            if depo_req:
                if depo_req.status != 'Pending':
                    return json.dumps({'Deposit Edit':'Failed'}), 400, {'ContentType':'application/json'}
                
                depo_req.amount = changeAmonut
                db.session.commit()
                 
            else:
                return json.dumps({'Deposit Edit':'Failed'}), 400, {'ContentType':'application/json'}

            
            return json.dumps({'Deposit Edit':'success'}), 200, {'ContentType':'application/json'}

        except:
            #THIS WILL BE FOR NEW REQUESTS, DEPOSIT TAKES JUST The First ARGUMENT, Can submit once every week
            depo_req = Deposit.query.filter_by(userID=user.id, status='Pending').all()
            
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
            new_deposit.userID = user.id
            
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

        del_req = Deposit.query.filter_by(userID=current_user.id, date=date, status='Pending').first()

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
