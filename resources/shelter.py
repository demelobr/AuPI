from flask_restful import Resource, reqparse
from models.shelter import ShelterModel
from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt

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
            return shelter.json(), 200
        
        return {'message':"Shelter '{}' not found.".format(shelter_name)}, 404
    
    @jwt_required()
    def put(self, shelter_name):
        arguments = received_data()
        data = arguments.parse_args()
        shelter = ShelterModel.find_shelter_by_name(data['shelter_name'])
        
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if shelter:
            if current_user.user_activated:
                shelter.update_shelter(**data)
                try:
                    shelter.save_shelter()
                except:
                    return {'message':'An internal error ocurred trying to save shelter.'}, 500
                
                return shelter.json(), 200
        
            return {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(current_user.user_username, current_user.user_email)}, 401
        
        return {'message':"Shelter '{}' not found.".format(shelter_name)}, 404

    @jwt_required()
    def delete(self, shelter_name):
        shelter = ShelterModel.find_shelter_by_name(shelter_name)
        
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if shelter:
            if current_user.user_activated:
                shelter.delete_shelter()
                return {'message':"Shelter '{}' deleted.".format(shelter_name)}
        
            return {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(current_user.user_username, current_user.user_email)}, 401

        return {'message':"User '{}' not found.".format(shelter_name)}, 404

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
    query_params.add_argument('limit', type=int, default=10, location="args")
    query_params.add_argument('offset', type=int, default=0, location="args")
    
    def get(self):
        filters = Shelters.query_params.parse_args()
        query = ShelterModel.query

        if filters['name']:
            query.filter(ShelterModel.shelter_name.like(filters['name']))
        if filters['accountable']:
            query.filter(ShelterModel.shelter_accountable.like(filters['accountable']))
        if filters['email']:
            query.filter(ShelterModel.shelter_email.like(filters['email']))
        if filters['phone_number']:
            query.filter(ShelterModel.shelter_phone_number.like(filters['phone_number']))
        if filters['address']:
            query.filter(ShelterModel.shelter_address.like(filters['address']))
        if filters['country']:
            query.filter(ShelterModel.shelter_country.like(filters['country']))
        if filters['state']:
            query.filter(ShelterModel.shelter_state.like(filters['state']))
        if filters['city']:
            query.filter(ShelterModel.shelter_city.like(filters['city']))
        if filters['limit']:
            query = query.limit(filters["limit"])
        if filters['offset']:
            query = query.offset(filters["offset"])
        
        return {"shelters": [shelter.json() for shelter in query]}

    @jwt_required()
    def post(self):
        arguments = received_data()
        data = arguments.parse_args()
        shelter = ShelterModel.find_shelter_by_name(data['shelter_name'])
        
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if current_user.user_activated:
            if shelter:
                return {"message": "The Shelter '{}' already exists.".format(data['shelter_name'])}, 400
            
            shelter = ShelterModel(**data)

            try:
                shelter.save_shelter()
            except:
                return {'message':'An internal error ocurred trying to save shelter.'}, 500
            
            return shelter.json(), 201
        
        return {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(current_user.user_username, current_user.user_email)}, 401