from flask_restful import Resource
from models.shelter import ShelterModel
from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt

def received_data():
    pass

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

        if current_user.user_activated:
            if shelter:
                shelter.update_shelter(**data)
                try:
                    shelter.save_shelter()
                except:
                    return {'message':'An internal error ocurred trying to save shelter.'}, 500
                
                return shelter.json(), 200

            return {'message':"Shelter '{}' not found.".format(shelter_name)}, 404
        
        return {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(current_user.user_username, current_user.user_email)}, 401
    
    @jwt_required()
    def delete(self, shelter_name):
        shelter = ShelterModel.find_shelter_by_name(shelter_name)
        
        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if current_user.user_activated:
            if shelter:
                shelter.delete()
                return {'message':"Shelter '{}' deleted.".format(shelter_name)}

            return {'message':"User '{}' not found.".format(shelter_name)}, 404
        
        return {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(current_user.user_username, current_user.user_email)}, 401


class Shelters(Resource):

    def get(self):
        pass

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