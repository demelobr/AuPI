from asyncio.windows_events import NULL
from email.policy import default
from flask_restful import Resource, reqparse
from models.request import RequestModel
from models.user import UserModel
from sql_alchemy import db
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
    query_params = reqparse.RequestParser()
    query_params.add_argument('datetime', type=str, default="", location="args")
    query_params.add_argument('owner', type=str, default="", location="args")
    query_params.add_argument('resource', type=str, default="", location="args")
    query_params.add_argument('method', type=str, default="", location="args")
    query_params.add_argument('url', type=str, default="", location="args")
    query_params.add_argument('message', type=str, default="", location="args")
    query_params.add_argument('code', type=str, default="", location="args")
    query_params.add_argument('limit', type=int, default=10, location="args")
    query_params.add_argument('offset', type=int, default=0, location="args") 

    @jwt_required()
    def get(self):
        filters = Requests.query_params.parse_args()
        all_filters = []

        if filters['datetime']:
            all_filters.append(RequestModel.request_datetime.like(filters['datetime']))
        if filters['owner']:
            all_filters.append(RequestModel.request_owner.like(filters['owner']))
        if filters['resource']:
            all_filters.append(RequestModel.request_resource.like(filters['resource']))
        if filters['method']:
            all_filters.append(RequestModel.request_method.like(filters['method']))
        if filters['url']:
            all_filters.append(RequestModel.request_url.like(filters['url']))
        if filters['message']:
            all_filters.append(RequestModel.request_message.like(filters['message']))
        if filters['code']:
            all_filters.append(RequestModel.resquest_code.like(filters['code']))
        
        if not filters['limit'] and not filters['offset']:
            query = db.session.query(RequestModel).filter(*all_filters).all()
        elif filters['limit'] and not filters['offset']:
            query = db.session.query(RequestModel).filter(*all_filters).limit(filters['limit']).all()
        elif not filters['limit'] and filters['offset']:
            query = db.session.query(RequestModel).filter(*all_filters).offset(filters['offset']).all()
        else:
            query = db.session.query(RequestModel).filter(*all_filters).limit(filters['limit']).offset(filters['offset']).all()

        return {"requests": [request.json() for request in query]}

    @jwt_required()
    def delete(self):
        pass