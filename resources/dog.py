from flask_restful import Resource, reqparse
from credentials import BASE_URL
from models.request import save_request, get_request_datetime
from models.dog import DogModel
from models.shelter import ShelterModel
from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt
from sql_alchemy import db

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
            response = {'message': 'Dog returned successfully.'}, 200
            request_datetime = get_request_datetime()
            save_request(request_datetime, "Undefined", "Dog", "GET", BASE_URL + "/dogs/" + str(dog_id), response)
            return dog.json(), 200
        
        response = {'message':"Dog with ID:{} not found.".format(dog_id)}, 404
        request_datetime = get_request_datetime()
        save_request(request_datetime, "Undefined", "Dog", "GET", BASE_URL + "/dogs/" + str(dog_id), response)
        return response

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

                        response = {'message':'Dog successfully edited.'}, 200
                        request_datetime = get_request_datetime()
                        save_request(request_datetime, current_user.user_username, "Dog", "PUT", BASE_URL + "/dogs/" + str(dog_id), response)
                        return dog.json(), 200

                    response = {'message': "Unable to save the dog as the birthday date format must be 'dd/mm/yyyy'."}, 401
                    request_datetime = get_request_datetime()
                    save_request(request_datetime, current_user.user_username, "Dog", "PUT", BASE_URL + "/dogs/" + str(dog_id), response)
                    return response

                response = {'message':"Shelter '{}' not found.".format(data['dog_shelter'])}, 404
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "Dog", "PUT", BASE_URL + "/dogs/" + str(dog_id), response)
                return response

            response = {'message':"User '{}' not confirmed. Access the email to activate your account".format(current_user.user_username)}, 401
            request_datetime = get_request_datetime()
            save_request(request_datetime, current_user.user_username, "Dog", "PUT", BASE_URL + "/dogs/" + str(dog_id), response)
            return response

        response = {'message':"Dog with ID:{} not found.".format(dog_id)}, 404
        request_datetime = get_request_datetime()
        save_request(request_datetime, current_user.user_username, "Dog", "PUT", BASE_URL + "/dogs/" + str(dog_id), response)
        return response

    @jwt_required()
    def delete(self, dog_id):
        dog = DogModel.find_dog_by_id(dog_id)

        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        if dog:
            if current_user.user_activated:
                dog.delete_dog()
                response = {'message':"Dog with ID:{} deleted.".format(dog_id)}, 200
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "Dog", "DELETE", BASE_URL + "/dogs/" + str(dog_id), response)
                return response

            response = {'message':"User '{}' not confirmed. Access the email to activate your account".format(current_user.user_username)}, 401
            request_datetime = get_request_datetime()
            save_request(request_datetime, current_user.user_username, "Dog", "DELETE", BASE_URL + "/dogs/" + str(dog_id), response)
            return response

        response = {'message':"Dog with ID:{} not found.".format(dog_id)}, 404
        request_datetime = get_request_datetime()
        save_request(request_datetime, current_user.user_username, "Dog", "DELETE", BASE_URL + "/dogs/" + str(dog_id), response)
        return response
        
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
        all_filters = []

        if filters['name']:
            all_filters.append(DogModel.dog_name.like(filters['name']))
        if filters['shelter']:
            all_filters.append(DogModel.dog_shelter.like(filters['shelter']))
        if filters['birth_date']:
            all_filters.append(DogModel.dog_birth_date.like(filters['birth_date']))
        if filters['gender']:
            all_filters.append(DogModel.dog_gender.like(filters['gender']))
        if filters['country']:
            all_filters.append(DogModel.dog_country.like(filters['country']))
        if filters['state']:
            all_filters.append(DogModel.dog_state.like(filters['state']))
        if filters['city']:
            all_filters.append(DogModel.dog_city.like(filters['city']))

        if not filters['limit'] and not filters['offset']:
            query = db.session.query(DogModel).filter(*all_filters).all()
        elif filters['limit'] and not filters['offset']:
            query = db.session.query(DogModel).filter(*all_filters).limit(filters['limit']).all()
        elif not filters['limit'] and filters['offset']:
            query = db.session.query(DogModel).filter(*all_filters).offset(filters['offset']).all()
        else:
            query = db.session.query(DogModel).filter(*all_filters).limit(filters['limit']).offset(filters['offset']).all()

        response = {'message':'Dogs returned successfully.'}, 200
        request_datetime = get_request_datetime()
        save_request(request_datetime, "Undefined", "Dogs", "GET", BASE_URL + "/dogs", response)
        return {"dogs": [dog.json() for dog in query]}, 200

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
                        response = {'message':'An internal error ocurred trying to save dog.'}, 500
                        request_datetime = get_request_datetime()
                        save_request(request_datetime, current_user.user_username, "Dogs", "POST", BASE_URL + "/dogs", response)
                        return response

                    response = {'message':'Dogs created successfully.'}, 201
                    request_datetime = get_request_datetime()
                    save_request(request_datetime, current_user.user_username, "Dogs", "POST", BASE_URL + "/dogs", response)
                    return dog.json(), 201

                response = {'message': "Unable to save the dog as the birthday date format must be 'dd/mm/yyyy'."}, 401   
                request_datetime = get_request_datetime()
                save_request(request_datetime, current_user.user_username, "Dogs", "POST", BASE_URL + "/dogs", response)
                return response

            response = {'message':"User '{}' not confirmed. Access the email to activate your account".format(current_user.user_username)}, 401
            request_datetime = get_request_datetime()
            save_request(request_datetime, current_user.user_username, "Dogs", "POST", BASE_URL + "/dogs", response)
            return response

        response = {'message':"Shelter '{}' not found.".format(data['dog_shelter'])}, 404
        request_datetime = get_request_datetime()
        save_request(request_datetime, current_user.user_username, "Dogs", "POST", BASE_URL + "/dogs", response)
        return response