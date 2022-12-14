from flask import make_response, render_template
from flask_restful import Resource, reqparse
from blacklist import BLACKLIST
from credentials import BASE_URL
from models.request import save_request, get_request_datetime
from models.user import UserModel
from hash import hash_password, check_hashed_password
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, decode_token
import re

def is_email(user_email):
    if re.search(r'[a-zA-Z0-9_-]+@[a-zA-Z0-9]+\.[a-zA-Z]{1,3}$', user_email):
        return True
    return False

def received_data(login=False):
    arguments = reqparse.RequestParser()
    arguments.add_argument('user_username', type=str, required=True, help="The field 'user_username' cannot be left blank.")
    if login:
        arguments.add_argument('user_name')
        arguments.add_argument('user_email')
        arguments.add_argument('user_phone_number')
    else:
        arguments.add_argument('user_name', type=str, required=True, help="The field 'user_name' cannot be left blank.")
        arguments.add_argument('user_email', type=str, required=True, help="The field 'user_email' cannot be left blank.")
        arguments.add_argument('user_phone_number', type=str, required=True, help="The field 'user_phone_number' cannot be left blank.")
    arguments.add_argument('user_password', type=str, required=True, help="The field 'user_password' cannot be left blank.")

    return arguments    

class User(Resource):
    
    @jwt_required()
    def get(self, user_username):
        user = UserModel.find_user_by_username(user_username)
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if user:
            if current_user.user_activated:            
                if jwt_id == user.user_jwt or current_user.user_sudo:
                    response = {'message': 'User returned successfully.'}, 200
                    request_datetime = get_request_datetime()
                    save_request(request_datetime, current_user.user_username, "User", "GET", BASE_URL + "/users/" + user_username, response)
                    return user.json(), 200
                
                response = {'message':"You do not have access to '{}' information".format(user_username)}, 203
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "User", "GET", BASE_URL + "/users/" + user_username, response)
                return response

            response = {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(current_user.user_username, current_user.user_email)}, 401
            request_datetime = get_request_datetime()
            save_request(request_datetime, current_user.user_username, "User", "GET", BASE_URL + "/users/" + user_username, response)
            return response

        response = {'message':"User '{}' not found".format(user_username)}, 404
        request_datetime = get_request_datetime()
        save_request(request_datetime, current_user.user_username, "User", "GET", BASE_URL + "/users/" + user_username, response)
        return response

    @jwt_required()
    def put(self, user_username):
        arguments = received_data()
        data = arguments.parse_args()
        user = UserModel.find_user_by_username(user_username)
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if user:
            if current_user.user_activated:
                if jwt_id == user.user_jwt or current_user.user_sudo:
                    if data['user_username'] != user_username and UserModel.find_user_by_username(data['user_username']):
                        response = {'message':"The User '{}' already exists.".format(data['user_username'])}, 400
                        request_datetime = get_request_datetime()
                        save_request(request_datetime, current_user.user_username, "User", "PUT", BASE_URL + "/users/" + user.user_username, response)
                        return response

                    if data['user_email'] != user.user_email and UserModel.find_user_by_email(data['user_email']):
                        response = {'message':"The Email '{}' is already registered in another account.".format(data['user_email'])}, 400
                        request_datetime = get_request_datetime()
                        save_request(request_datetime, current_user.user_username, "User", "PUT", BASE_URL + "/users/" + user.user_username, response)
                        return response

                    if not is_email(data['user_email']):
                        response = {'message':"The email '{}' sent is not valid.".format(data['user_email'])}
                        request_datetime = get_request_datetime()
                        save_request(request_datetime, current_user.user_username, "User", "PUT", BASE_URL + "/users/" + user.user_username, response)
                        return response

                    if data['user_email'] != user.user_email:
                        user.user_activated = False

                    data['user_password'] = hash_password(data['user_password'])
                    
                    user.user_code_confirm_generator()
                    
                    user.update_user(**data)
                    
                    try:
                        user.save_user()
                        if user.user_activated == False:
                            confirmation_link = "{}/confirm/{}/{}".format( BASE_URL, data['user_username'], user.user_code_confirm)
                            user.send_confirmation_email(confirmation_link)
                    except:
                        return {'message':'An internal error ocurred trying to save user.'}, 500
                    
                    response = {'message': 'User edited successfully.'}, 200
                    request_datetime = get_request_datetime()
                    save_request(request_datetime, current_user.user_username, "User", "PUT", BASE_URL + "/users/" + user.user_username, response)
                    return user.json(), 200
                    
                response = {'message':"You do not have access to edit '{}' information".format(user_username)}, 203
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "User", "PUT", BASE_URL + "/users/" + user.user_username, response)
                return response

            response = {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(current_user.user_username, current_user.user_email)}, 401
            request_datetime = get_request_datetime()
            save_request(request_datetime, current_user.user_username, "User", "PUT", BASE_URL + "/users/" + user.user_username, response)
            return response

        response = {'message':"User '{}' not found.".format(user_username)}, 404
        request_datetime = get_request_datetime()
        save_request(request_datetime, current_user.user_username, "User", "PUT", BASE_URL + "/users/" + user.user_username, response)
        return response        

    @jwt_required()
    def delete(self, user_username):
        user = UserModel.find_user_by_username(user_username)
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if user:    
            if current_user.user_activated:
                if jwt_id == user.user_jwt or current_user.user_sudo:
                    user.delete_user()
                    if not current_user.user_sudo:
                        BLACKLIST.add(jwt_id)

                    response = {'message':"User '{}' deleted.".format(user_username)}, 200
                    request_datetime = get_request_datetime()
                    save_request(request_datetime, current_user.user_username, "User", "DEL", BASE_URL + "/users/" + user_username, response)
                    return response
                
                response = {'message':"You do not have access to delete '{}' information".format(user_username)}, 203
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "User", "DEL", BASE_URL + "/users/" + user_username, response)
                return response

            response = {'message':"User '{}' not confirmed. Access the email to activate your account".format(current_user.user_username)}, 401
            request_datetime = get_request_datetime()
            save_request(request_datetime, current_user.user_username, "User", "DEL", BASE_URL + "/users/" + user_username, response)
            return response

        response = {'message':"User '{}' not found.".format(user_username)}, 404
        request_datetime = get_request_datetime()
        save_request(request_datetime, current_user.user_username, "User", "DEL", BASE_URL + "/users/" + user_username, response)
        return response

class UserRegister(Resource):
    
    def post(self):
        arguments = received_data()
        data = arguments.parse_args()

        if UserModel.find_user_by_username(data['user_username']):
            return {'message':"The User '{}' already exists.".format(data['user_username'])}, 400

        if not data.get('user_email') or data.get('user_email') is None:
            return {'message':"The field 'user_email' cannot be left blank."}, 400

        if not is_email(data['user_email']):
            return {'message':"The email '{}' sent is not valid.".format(data['user_email'])}

        if UserModel.find_user_by_email(data['user_email']):
            return {'message':"The Email '{}' is already registered in another account.".format(data['user_email'])}, 400

        data['user_password'] = hash_password(data['user_password'])

        user = UserModel(**data)
        user.user_code_confirm_generator()
        
        try:
            user.save_user()
            confirmation_link = "{}/confirm/{}/{}".format( BASE_URL, data['user_username'], user.user_code_confirm)
            user.send_confirmation_email(confirmation_link)
            
            response = {
                    'message':"User '{}' created successfully! Confirm your account by accessing your registered email.".format(data['user_username']), 
                    'confirmation_link': confirmation_link                
            }, 201
            request_datetime = get_request_datetime()
            save_request(request_datetime, data['user_username'], "UserRegister","POST", BASE_URL + "/register", response)
            return response
        
        except:
            return {'message':'An internal error ocurred trying to save user.'}, 500

class UserLogin(Resource):

    @classmethod
    def post(cls):
        arguments = received_data(True)
        data = arguments.parse_args()
        user = UserModel.find_user_by_username(data['user_username'])

        if user: 
            if check_hashed_password(data['user_password'], user.user_password):
                if user.user_activated:
                    access_token = create_access_token(identity=user.user_id)
                    user.user_jwt = decode_token(access_token)['jti']

                    try:
                        user.save_user()
                        response = {'message': 'Login successfully!', 'access_token':access_token}, 200
                        request_datetime = get_request_datetime()
                        save_request(request_datetime, user.user_username, "UserLogin", "POST", BASE_URL + "/login", response)
                        return response
                    except:
                        response = {'message':'An internal error ocurred trying to save user.'}, 500
                        request_datetime = get_request_datetime()
                        save_request(request_datetime, user.user_username, "UserLogin", "POST", BASE_URL + "/login", response)
                        return response

                response = {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(user.user_username, user.user_email)}, 401
                request_datetime = get_request_datetime()
                save_request(request_datetime, user.user_username, "UserLogin", "POST", BASE_URL + "/login", response)
                return response    

            response = {'message':'Username or password is incorrect.'}, 401
            request_datetime = get_request_datetime()
            save_request(request_datetime, user.user_username, "UserLogin", "POST", BASE_URL + "/login", response)
            return response

        return {'massage':"The User '{}' not exists.".format(data['user_username'])}, 400

class UserLogout(Resource):

    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)
        BLACKLIST.add(jwt_id)
        response = {'message':'Logged out successfully!'}, 200
        request_datetime = get_request_datetime()
        save_request(request_datetime, current_user.user_username, "UserLogout", "POST", BASE_URL + "/logout", response)
        return response

class UserConfirm(Resource):

    @classmethod
    def get(cls, user_username, user_code_confirm):
        user = UserModel.find_user_by_username(user_username)

        if not user:
            return {'message':"User '{}' not found.".format(user_username)}

        if user and user.user_code_confirm == user_code_confirm:
            user.user_activated = True
            
            try:
                user.save_user()
                return make_response(render_template('email_confirmed.html', user=user, base_url=BASE_URL))
            except:
                return {'message':'An internal error ocurred trying to save user.'}, 500    