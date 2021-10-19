import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError,AccessError
from src import config
from src.other import clear_v1
import src.other as other
from json import dumps
from src.auth import auth_register_v1,auth_login_v1,auth_logout_v1
from src.data_store import data_store
from src.channels import channels_listall_v1
import pickle

try:
    store = pickle.load(open("datastore.p", "rb"))
    #clear sessions
    for user in store['users']:
        user['sessions'] = []
    data_store.set(store)
except Exception:
    pass

def quit_gracefully(*args):
    '''For coverage'''
    exit(0)

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

#### NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

# Return the datastore
@APP.route("/get_data", methods=['GET'])
def get_all_data():
    return dumps(data_store.get())

# Reset database through clearing the dictionaries

@APP.route("/clear/v1", methods=['DELETE'])
def delete_clear():
    clear_v1()
    return dumps({})

# Registers a new user from given JSON data in Body
@APP.route("/auth/register/v2", methods=['POST'])
def post_auth_register():
    request_data = request.get_json()
    print(request_data)
    auth_result = auth_register_v1(
        request_data['email'],
        request_data['password'],
        request_data['name_first'],
        request_data['name_last']
    )
    data_store.save()
    return dumps(auth_result)

# Login an account through a post request
@APP.route("/auth/login/v2", methods=['POST'])
def post_auth_login():
    request_data = request.get_json()
    auth_result = auth_login_v1(
        request_data['email'],
        request_data['password']
    )
    data_store.save()
    return dumps(auth_result)

# Logout an account through a post request
# do we handle invalid tokens (see result of auth_logout_v1?
@APP.route("/auth/logout/v1", methods=['POST'])
def post_auth_logout():
    request_data = request.get_json()
    _ = auth_logout_v1(
        request_data['token']
    )
    data_store.save()
    return dumps({})

# Returns all the channels in the datastore
@APP.route("/channels/listall/v2", methods=['GET'])
def get_channels_listall():
    data = request.args.get('token')
    channels = channels_listall_v1(data)
    return dumps(channels)

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)
    APP.run(port=config.port, debug=True)
