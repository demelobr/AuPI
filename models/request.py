from sql_alchemy import db

class RequestModel(db.Model):
    __tablename__ = 'requests'

    request_id = db.Column(db.Integer, primary_key=True)
    request_datetime = db.Column(db.String, nullable=False)
    request_owner = db.Column(db.String(20), db.ForeignKey('users.user_username'), nullable=False)
    request_method = db.Column(db.String(20), nullable=False)
    request_url = db.Column(db.String, nullable=False)
    resquest_response = db.Column(db.String(3), nullable=False)

    def __init__(self, request_datetime, request_owner, request_method, request_url, resquest_response):
        self.request_datetime = request_datetime
        self.request_owner = request_owner
        self.request_method = request_method
        self.request_url = request_url
        self.resquest_response = resquest_response
    
    def json(self):
        return{
            'request_id': self.request_id,
            'request_datetime': self.request_datetime,
            'request_owner': self.request_owner,
            'request_method': self.request_method,
            'request_url': self.request_url,
            'resquest_response': self.resquest_response
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