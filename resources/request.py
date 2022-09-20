from flask_restful import Resource
from models.request import RequestModel
from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt

class Request(Resource):

    @jwt_required()
    def get(self, request_id):
        request = RequestModel.find_request_by_id(request_id)

        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        current_user.user_sudo = True
        
        if current_user.user_sudo:
            if request:
                return request.json(), 200
            
            return {'message':"Request with ID:{} not found.".format(request_id)}, 404
    
        return {'message':"The user '{}' is not authorized for this resource.".format(current_user.user_username)}, 203

    @jwt_required()
    def delete(self, request_id):
        request = RequestModel.find_request_by_id(request_id)

        jwt_id = get_jwt()['jti']
        current_user = UserModel.find_user_by_jwt(jwt_id)

        current_user.user_sudo = True

        if current_user.user_sudo:
            if request:
                request.delete_request()
                return {'message':"Request with ID:{} deleted.".format(request_id)}
                    
            return {'message':"Request with ID:{} not found.".format(request_id)}, 404

        return {'message':"The user '{}' is not authorized for this resource.".format(current_user.user_username)}, 203


class Requests(Resource):

    @jwt_required()
    def get():
        pass

    @jwt_required()
    def delete():
        pass