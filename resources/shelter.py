from email.policy import default
from flask_restful import Resource, reqparse
from credentials import BASE_URL
from models.request import save_request, get_request_datetime
from models.shelter import ShelterModel
from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt
from sql_alchemy import db

def received_data():
    arguments = reqparse.RequestParser()
    arguments.add_argument('shelter_name', type=str, required=True, help="The field 'shelter_name' cannot be left blank.")
    arguments.add_argument('shelter_accountable', type=str, required=True, help="The field 'shelter_accountable' cannot be left blank.")
    arguments.add_argument('shelter_email', type=str, required=True, help="The field 'shelter_email' cannot be left blank.")
    arguments.add_argument('shelter_phone_number', type=str, required=True, help="The field 'shelter_phone_number' cannot be left blank.")
    arguments.add_argument('shelter_address', type=str, required=True, help="The field 'shelter_address' cannot be left blank.")
    arguments.add_argument('shelter_country', type=str, required=True, help="The field 'shelter_country' cannot be left blank.")
    arguments.add_argument('shelter_state', type=str, required=True, help="The field 'shelter_state' cannot be left blank.")
    arguments.add_argument('shelter_city', type=str, required=True, help="The field 'shelter_city' cannot be left blank.")

    return arguments

class Shelter(Resource):
    
    def get(self, shelter_name):
        shelter = ShelterModel.find_shelter_by_name(shelter_name)
  
        if shelter:
            response = {'message': 'Shelter returned successfully.'}, 200
            request_datetime = get_request_datetime()
            save_request(request_datetime, "Undefined", "Shelter", "GET", BASE_URL + "/shelters/"  + shelter_name, response)
            return shelter.json(), 200

        response = {'message':"Shelter '{}' not found.".format(shelter_name)}, 404
        request_datetime = get_request_datetime()
        save_request(request_datetime, "Undefined", "Shelter", "GET", BASE_URL + "/shelters/" + shelter_name, response)
        return response

    @jwt_required()
    def put(self, shelter_name):
        arguments = received_data()
        data = arguments.parse_args()
        shelter = ShelterModel.find_shelter_by_name(shelter_name)
        
        print(shelter)

        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if shelter:
            if current_user.user_activated:
                shelter.update_shelter(**data)
                try:
                    shelter.save_shelter()
                except:
                    return {'message':'An internal error ocurred trying to save shelter.'}, 500
                
                response = {'message':'Shelter successfully edited.'}, 200
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "Shelter", "PUT", BASE_URL + "/shelters/" + shelter_name, response)
                return shelter.json(), 200

            response = {'message':"User '{}' not confirmed. Access the email to activate your account".format(current_user.user_username)}, 401
            request_datetime = get_request_datetime()  
            save_request(request_datetime, current_user.user_username, "Shelter", "PUT", BASE_URL + "/shelters/" + shelter_name, response)
            return response

        response = {'message':"Shelter '{}' not found.".format(shelter_name)}, 404
        request_datetime = get_request_datetime()  
        save_request(request_datetime, current_user.user_username, "Shelter", "PUT", BASE_URL + "/shelters/" + shelter_name, response)
        return response

    @jwt_required()
    def delete(self, shelter_name):
        shelter = ShelterModel.find_shelter_by_name(shelter_name)
        
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if shelter:
            if current_user.user_activated:
                shelter.delete_shelter()
                response = {'message':"Shelter '{}' deleted.".format(shelter_name)}
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "Shelter", "DELETE", BASE_URL + "/shelters/" + shelter_name, response)
                return response

            response = {'message':"User '{}' not confirmed. Access the email to activate your account".format(current_user.user_username)}, 401
            request_datetime = get_request_datetime()
            save_request(request_datetime, current_user.user_username, "Shelter", "DELETE", BASE_URL + "/shelters/" + shelter_name, response)
            return response

        response = {'message':"User '{}' not found.".format(shelter_name)}, 404
        request_datetime = get_request_datetime()
        save_request(request_datetime, current_user.user_username, "Shelter", "DELETE", BASE_URL + "/shelters/" + shelter_name, response)
        return response

class Shelters(Resource):

    query_params = reqparse.RequestParser()
    query_params.add_argument('name', type=str, default="", location="args")
    query_params.add_argument('accountable', type=str, default="", location="args")
    query_params.add_argument('email', type=str, default="", location="args")
    query_params.add_argument('phone_number', type=str, default="", location="args")
    query_params.add_argument('address', type=str, default="", location="args")
    query_params.add_argument('country', type=str, default="", location="args")
    query_params.add_argument('state', type=str, default="", location="args")
    query_params.add_argument('city', type=str, default="", location="args")
    query_params.add_argument('verified', type=bool, default=False,location="args")
    query_params.add_argument('limit', type=int, default=10, location="args")
    query_params.add_argument('offset', type=int, default=0, location="args")
    
    def get(self):
        filters = Shelters.query_params.parse_args()
        all_filters = []

        if filters['name']:
            all_filters.append(ShelterModel.shelter_name.like(filters['name']))
        if filters['accountable']:
            all_filters.append(ShelterModel.shelter_accountable.like(filters['accountable']))
        if filters['email']:
            all_filters.append(ShelterModel.shelter_email.like(filters['email']))
        if filters['phone_number']:
            all_filters.append(ShelterModel.shelter_phone_number.like(filters['phone_number']))
        if filters['address']:
            all_filters.append(ShelterModel.shelter_address.like(filters['address']))
        if filters['country']:
            all_filters.append(ShelterModel.shelter_country.like(filters['country']))
        if filters['state']:
            all_filters.append(ShelterModel.shelter_state.like(filters['state']))
        if filters['city']:
            all_filters.append(ShelterModel.shelter_city.like(filters['city']))
        if filters['verified']:
            all_filters.append(ShelterModel.shelter_verified == filters['verified'])

        if not filters['limit'] and not filters['offset']:
            query = db.session.query(ShelterModel).filter(*all_filters).all()
        elif filters['limit'] and not filters['offset']:
            query = db.session.query(ShelterModel).filter(*all_filters).limit(filters['limit']).all()
        elif not filters['limit'] and filters['offset']:
            query = db.session.query(ShelterModel).filter(*all_filters).offset(filters['offset']).all()
        else:
            query = db.session.query(ShelterModel).filter(*all_filters).limit(filters['limit']).offset(filters['offset']).all()

        response = {'message':'Sheltrs returned successfully.'}, 200
        request_datetime = get_request_datetime()
        save_request(request_datetime, "Undefined", "Shelters", "GET", BASE_URL + "/shelters", response)
        return {"shelters": [shelter.json() for shelter in query]}, 200

    @jwt_required()
    def post(self):
        arguments = received_data()
        data = arguments.parse_args()
        shelter = ShelterModel.find_shelter_by_name(data['shelter_name'])
        
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if current_user.user_activated:
            if shelter:
                response = {"message": "The Shelter '{}' already exists.".format(data['shelter_name'])}, 400
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "Shelters", "POST", BASE_URL + "/shelters", response)
                return response

            shelter = ShelterModel(**data)

            try:
                shelter.save_shelter()
            except:
                response = {'message':'An internal error ocurred trying to save shelter.'}, 500
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "Shelters", "POST", BASE_URL + "/shelters", response)
                return response

            response = {'message':'Shelter created successfully.'}, 201
            request_datetime = get_request_datetime()
            save_request(request_datetime, current_user.user_username, "Shelters", "POST", BASE_URL + "/shelters", response)
            return shelter.json(), 201

        response = {'message':"User '{}' not confirmed. Access the email to activate your account".format(current_user.user_username)}, 401
        request_datetime = get_request_datetime()
        save_request(request_datetime, current_user.user_username, "Shelters", "POST", BASE_URL + "/shelters", response)
        return response

class ShelterVerified(Resource):
    
    @jwt_required()
    def post(cls, shelter_name):
        shelter = ShelterModel.find_shelter_by_name(shelter_name)
        
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        current_user.user_sudo = True
        
        if current_user.user_activated:
            if current_user.user_sudo:
                if shelter:
                    shelter.verified_shelter()
                    response = {'message':'Shelter check done.'}, 200
                    request_datetime = get_request_datetime()
                    save_request(request_datetime, current_user.user_username, "ShelterVirified", "POST", BASE_URL + "/shelters/verified/" + shelter_name, response)
                    return response
                
                response = {"message": "The Shelter '{}' already exists.".format(shelter_name)}, 400
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "ShelterVirified", "POST", BASE_URL + "/shelters/verified/" + shelter_name, response)
                return response
            
            response = {'message':"You do not have access to verified '{}' information".format(shelter_name)}, 203
            request_datetime = get_request_datetime()
            save_request(request_datetime, current_user.user_username, "ShelterVirified", "POST", BASE_URL + "/shelters/verified/" + shelter_name, response)
            return response
        
        response = {'message':"User '{}' not confirmed. Access the email to activate your account".format(current_user.user_username)}, 401
        request_datetime = get_request_datetime()
        save_request(request_datetime, current_user.user_username, "ShelterVirified", "POST", BASE_URL + "/shelters/verified/" + shelter_name, response)
        return response