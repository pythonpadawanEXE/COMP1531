import sys
import signal
from json import dumps
from flask import Flask, request, jsonify
from flask_cors import CORS
from src import config
from src.error import InputError, AccessError
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1
from src.channel import channel_messages_v1
from src.channels import channels_create_v1, channels_list_v1
from src.other import check_valid_token, clear_v1
from src.data_store import data_store
from src.message import message_send_v1
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

# Auth Routes

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

#logout an account through a post request
@APP.route("/auth/logout/v1", methods=['POST'])
def post_auth_logout():
    request_data = request.get_json()
    _ = auth_logout_v1(
        request_data['token']
    )
    data_store.save()
    return dumps({})

# Channel Routes
@APP.route("/channel/messages/v2", methods=['GET'])
def get_channel_messages():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')
    channel_messages = channel_messages_v1(
        token,
        channel_id,
        start
    )
    data_store.save()
    return dumps(channel_messages)
# Channels Routes

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    request_data = request.get_json()
    token = request_data['token']
    name = request_data['name']
    is_public = request_data['is_public'] == True
    decoded_token = check_valid_token(token)
    return dumps(channels_create_v1(decoded_token['auth_user_id'], name, is_public))

# Returns all the channels in the datastore
@APP.route("/channels/listall/v2", methods=['GET'])
def get_channels_listall():
    data = request.args.get('token')
    channels = channels_listall_v1(data)
    return dumps(channels)

# Returns all the channels that the caller is a member of
@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    token = request.args.get('token')
    decoded_token = check_valid_token(token)
    return dumps(channels_list_v1(decoded_token['auth_user_id']))

# Message Routes
@APP.route("/message/send/v1", methods=['POST'])
def post_message_send():
    request_data = request.get_json()
    message_id = message_send_v1(
        request_data['token'],
        request_data['channel_id'],
        request_data['message']
    )
    data_store.save()
    return dumps(message_id)
# Dm Routes

# Other routes

@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route("/get_data", methods=['GET'])
def get_all_data():
    return dumps(data_store.get())

# Reset database through clearing the dictionaries
@APP.route("/clear/v1", methods=['DELETE'])
def delete_clear():
    clear_v1()
    return dumps({})

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)
    APP.run(port=config.port)
