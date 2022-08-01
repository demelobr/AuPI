from email.policy import default
from sql_alchemy import db
import string
import random

class UserModel(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.String(20), nulllable=False, unique=True)
    user_email = db.Column(db.String(80), nulllable=False, unique=True)
    user_password = db.Column(db.String(40), nulllable=False)
    user_activated = db.Column(db.Boolean, default=False)
    user_sudo = db.Column(db.Boolean, default=False)
    user_jwt = db.Column(db.String(40), default="")
    user_code_confirm = db.Column(db.String(30), default="")

    def __init__(self, user_username, user_email, user_password):
        self.user_username = user_username
        self.user_email = user_email
        self.user_password = user_password
    
    def json(self):
        return {
            'user_id': self.user_id,
            'user_username': self.user_username,
            'user_activated': self.user_activated
        }
    
    @classmethod
    def find_user_by_username(cls, user_username):
        user = cls.query.filter_by(user_username=user_username).first()
        if user:
            return user
        return False        

    @classmethod
    def find_user_by_email(cls, user_email):
        user = cls.query.filter_by(user_email=user_email).first()
        if user:
            return user
        return False

    @classmethod
    def find_user_by_jwt(cls, user_jwt):
        user = cls.query.filter_by(user_jwt=user_jwt).first()
        if user:
            return user
        return False  

    def user_code_confirm_generator(self, size=20, chars=string.ascii_uppercase + string.digits):
        self.user_code_confirm = ''.join(random.choice(chars) for _ in range(size))

    def save_user(self):
        db.session.add(self)
        db.session.commit()

    def update_user(self):
        self.user_username
        self.user_email
        self.user_password

    def delete_user(self):
        db.session.delete(self)
        db.session.commit()    
