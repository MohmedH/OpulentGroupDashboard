from app import db
from app.base.models import User, Portfolio
import json


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