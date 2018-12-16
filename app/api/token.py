from flask import g, jsonify
from flask_httpauth import HTTPTokenAuth
from mongoengine.errors import DoesNotExist

from . import api
from ..models import User
from .errors import Unauthorized

auth = HTTPTokenAuth(scheme='Token')


@auth.verify_token
def verify_token(token):
    try:
        user = User.objects.get(token=token)
        g.current_user = user.token
        return True
    except DoesNotExist:
        return False


@auth.error_handler
def authentication_error():
    raise Unauthorized(message='Invalid Token')


@api.route('/tokens/<email>')
def get_token(email):
    # Send User Token
    user = User.objects.get(email=email)
    return jsonify({'token': user.token})
