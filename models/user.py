from sql_alchemy import db
from email.message import EmailMessage
from hash import hash_password
from credentials import EMAIL_ADDRESS, EMAIL_PASSWORD, USER_NAME, USER_USERNAME, USER_EMAIL, USER_PHONE_NUMBER, USER_PASSWORD
import string
import random
import os
import smtplib

class UserModel(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    user_username = db.Column(db.String(20), nullable=False, unique=True)
    user_name = db.Column(db.String(40), nullable=False)
    user_email = db.Column(db.String(80), nullable=False, unique=True)
    user_phone_number = db.Column(db.String(20), nullable=False)
    user_password = db.Column(db.String(40), nullable=False)
    user_activated = db.Column(db.Boolean, default=False)
    user_sudo = db.Column(db.Boolean, default=False)
    user_jwt = db.Column(db.String(40), default="")
    user_code_confirm = db.Column(db.String(30), default="")

    def __init__(self, user_username, user_name, user_email, user_phone_number, user_password):
        self.user_username = user_username
        self.user_name = user_name
        self.user_email = user_email
        self.user_phone_number = user_phone_number
        self.user_password = user_password
    
    def json(self):
        return {
            'user_username': self.user_username,
            'user_name': self.user_name,
            'user_email': self.user_email,
            'user_phone_number': self.user_phone_number,
            'user_activated': self.user_activated
        }
    
    @classmethod
    def create_admin(cls):
        global USER_PASSWORD
        USER_PASSWORD = hash_password(USER_PASSWORD)
        admin = UserModel(USER_USERNAME, USER_NAME, USER_EMAIL, USER_PHONE_NUMBER, USER_PASSWORD)
        admin.user_activated = True
        admin.user_sudo = True

        try:
            admin.save_user()
        except:
            return {'message':'An internal error ocurred trying to create admin.'}, 500

        return {'message': 'User admin was created successfully!'}, 201


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

    def send_confirmation_email(self, confirmation_link):

        '''EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
        EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')'''

        msg = EmailMessage()
        msg['Subject'] = 'AuPi - Email de confirmação de conta!'
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = self.user_email

        msg.set_content("Olá Aumigo {}! Clique no link para confirmar sua conta '{}': {}".format(self.user_name, self.user_username, confirmation_link))

        msg.add_alternative("""\
        <!DOCTYPE html>
        <html>
            <body>
                <h1>Olá Aumigo {}!</h1>
                <p>Para confirmar sua conta '{}' <a style = "color:#39ff14" href="{}">clique aqui</a>.</p>
            </body>
        </html>
        """.format(self.user_name, self.user_username, confirmation_link), subtype='html')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)        

    def save_user(self):
        db.session.add(self)
        db.session.commit()

    def update_user(self, user_username, user_name, user_email, user_phone_number, user_password):
        self.user_username = user_username
        self.user_name = user_name
        self.user_email = user_email
        self.user_phone_number = user_phone_number
        self.user_password = user_password

    def delete_user(self):
        db.session.delete(self)
        db.session.commit()    