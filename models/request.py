from sql_alchemy import db
import datetime

def get_request_datetime():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%d/%m/%Y %H:%M:%S.%f")[:-3]

def save_request(datetime, owner, resouce, method, url, response):
    request = RequestModel(datetime, owner, resouce, method, url, response[0]['message'], response[1])

    try:
        request.save_request()
    except:
        print("An internal error ocurred trying to save request.")

class RequestModel(db.Model):
    __tablename__ = 'requests'

    request_id = db.Column(db.Integer, primary_key=True)
    request_datetime = db.Column(db.String, nullable=False)
    request_owner = db.Column(db.String(20), db.ForeignKey('users.user_username'), nullable=False)
    request_resource = db.Column(db.String, nullable=False)
    request_method = db.Column(db.String(20), nullable=False)
    request_url = db.Column(db.String, nullable=False)
    request_message = db.Column(db.String, nullable=False)
    resquest_code = db.Column(db.String(3), nullable=False)

    def __init__(self, request_datetime, request_owner, request_resource, request_method, request_url, request_message, resquest_code):
        self.request_datetime = request_datetime
        self.request_owner = request_owner
        self.request_resource = request_resource
        self.request_method = request_method
        self.request_url = request_url
        self.request_message = request_message
        self.resquest_code = resquest_code
    
    def json(self):
        return{
            'request_id': self.request_id,
            'request_datetime': self.request_datetime,
            'request_owner': self.request_owner,
            'request_resource': self.request_resource,
            'request_method': self.request_method,
            'request_url': self.request_url,
            'request_message': self.request_message,
            'resquest_code': self.resquest_code
        }
    
    @classmethod
    def find_request_by_id(cls, request_id):
        request = cls.query.filter_by(request_id=request_id).first()
        if request:
            return request
        return False

    def save_request(self):
        db.session.add(self)
        db.session.commit()
    
    def delete_request(self):
        db.session.delete(self)
        db.session.commit()