from flask_restful import Resource, reqparse
from models.dog import DogModel
from models.shelter import ShelterModel
from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt

def received_data():
    arguments = reqparse.RequestParser()
    arguments.add_argument('dog_name', type=str, required=True, help="The field 'dog_name' cannot be left blank.")
    arguments.add_argument('dog_shelter', type=str, required=True, help="The field 'dog_shelter' cannot be left blank.")
    arguments.add_argument('dog_birth_date', type=str, required=True, help="The field 'dog_birth_date' cannot be left blank.")
    arguments.add_argument('dog_gender', type=str, required=True, help="The field 'dog_gender' cannot be left blank.")

    return arguments

class Dog(Resource):

    def get(self, dog_id):
        dog = DogModel.find_dog_by_id(dog_id)

        if dog:
            return dog.json(), 200
        
        return {'message':"Dog with ID:{} not found.".format(dog_id)}, 404

    @jwt_required()
    def put(self, dog_id):
        arguments = received_data()
        data = arguments.parse_args() 
        shelter = ShelterModel.find_shelter_by_name(data['dog_shelter'])
        dog = DogModel.find_dog_by_id(dog_id)

        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)
        
        if dog:
            if current_user.user_activated:
                if shelter:
                    dog.update_dog(**data)
                    if dog.is_date():
                        try:
                            dog.save_dog()
                        except:
                            return {'message':'An internal error ocurred trying to save dog.'}, 500

                        return dog.json(), 200

                    return {'message': "Unable to save the dog as the birthday date format must be 'dd/mm/yyyy'."}, 401
                
                return {'message':"Shelter '{}' not found.".format(data['dog_shelter'])}, 404

            return {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(current_user.user_username, current_user.user_email)}, 401

        return {'message':"Dog with ID:{} not found.".format(dog_id)}, 404

    @jwt_required()
    def delete(self, dog_id):
        dog = DogModel.find_dog_by_id(dog_id)

        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if dog:
            if current_user.user_activated:
                dog.delete_dog()
                return {'message':"Dog with ID:{} deleted.".format(dog_id)}

            return {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(current_user.user_username, current_user.user_email)}, 401

        return {'message':"Dog with ID:{} not found.".format(dog_id)}, 404
        
class Dogs(Resource):
    query_params = reqparse.RequestParser()
    query_params.add_argument('name', type=str, default="", location="args")
    query_params.add_argument('shelter', type=str, default="", location="args")
    query_params.add_argument('birth_date', type=str, default="", location="args")
    query_params.add_argument('gender', type=str, default="", location="args")
    query_params.add_argument('country', type=str, default="", location="args")
    query_params.add_argument('state', type=str, default="", location="args")
    query_params.add_argument('city', type=str, default="", location="args")
    query_params.add_argument('limit', type=int, default=10, location="args")
    query_params.add_argument('offset', type=int, default=0, location="args")    

    def get(self):
        filters = Dogs.query_params.parse_args()
        query = DogModel.query

        if filters['name']:
            query.filter(DogModel.dog_name.like(filters['name']))
        if filters['shelter']:
            query.filter(DogModel.dog_shelter.like(filters['shelter']))
        if filters['birth_date']:
            query.filter(DogModel.dog_birth_date.like(filters['birth_date']))
        if filters['gender']:
            query.filter(DogModel.dog_gender.like(filters['gender']))
        if filters['country']:
            query.filter(DogModel.dog_country.like(filters['country']))
        if filters['state']:
            query.filter(DogModel.dog_state.like(filters['state']))
        if filters['city']:
            query.filter(DogModel.dog_city.like(filters['city']))
        if filters['limit']:
            query = query.limit(filters["limit"])
        if filters['offset']:
            query = query.offset(filters["offset"])
        
        return {"dogs": [dog.json() for dog in query]}

    @jwt_required()
    def post(self):
        arguments = received_data()
        data = arguments.parse_args() 
        shelter = ShelterModel.find_shelter_by_name(data['dog_shelter'])

        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if shelter:    
            if current_user.user_activated:
                dog = DogModel(**data)
                dog.set_dog_location()
                if dog.is_date():
                    try:
                        dog.save_dog()
                    except:
                        return {'message':'An internal error ocurred trying to save dog.'}, 500

                    return dog.json(), 201

                return {'message': "Unable to save the dog as the birthday date format must be 'dd/mm/yyyy'."}, 401   

            return {'message':"User '{}' not confirmed. Access the email '{}' to activate your account".format(current_user.user_username, current_user.user_email)}, 401

        return {'message':"Shelter '{}' not found.".format(data['dog_shelter'])}, 404