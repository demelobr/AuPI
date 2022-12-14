from flask import Flask, jsonify, render_template
from flask_restful import Api
from blacklist import BLACKLIST
from models.user import UserModel
from models.request import save_request, get_request_datetime
from resources.dog import Dogs, Dog, DogVerified
from resources.shelter import Shelter, Shelters, ShelterVerified
from resources.user import User, UserConfirm, UserRegister, UserLogin, UserLogout
from resources.request import Request, Requests
from flask_jwt_extended import JWTManager
from credentials import SECRET_KEY
import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = SECRET_KEY
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=14)
api = Api(app)
jwt = JWTManager(app)


@app.before_first_request
def startup():
    db.create_all()
    response = UserModel.create_admin()
    request_datetime = get_request_datetime()
    save_request(request_datetime, "system", "undefined", "undefined", "undefined", response)

@jwt.token_in_blocklist_loader
def blacklist_verify(self, token):
    return token['jti'] in BLACKLIST

@jwt.revoked_token_loader
def invalid_access_token(jwt_header, jwt_payload):
    return jsonify({'message':'You have been logged out.'}), 401

@app.route('/')
def index():
    return render_template('index.html')

api.add_resource(Shelters, '/shelters')
api.add_resource(Shelter, '/shelters/<string:shelter_name>')
api.add_resource(ShelterVerified, '/shelters/verified/<string:shelter_name>')
api.add_resource(Dogs, '/dogs')
api.add_resource(Dog, '/dogs/<int:dog_id>')
api.add_resource(DogVerified, '/dogs/verified/<int:dog_id>')
api.add_resource(User, '/users/<string:user_username>')
api.add_resource(UserRegister, '/register')
api.add_resource(UserLogin, '/login')
api.add_resource(UserLogout, '/logout')
api.add_resource(UserConfirm, '/confirm/<string:user_username>/<string:user_code_confirm>')
api.add_resource(Requests, '/requests')
api.add_resource(Request, '/requests/<int:request_id>')

if __name__ == '__main__':
    from sql_alchemy import db
    db.init_app(app)
    app.run(debug=True)