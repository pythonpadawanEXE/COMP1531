import sys
import signal
from json import dumps
from flask import Flask, request, jsonify
from flask_cors import CORS
from src import config
from src.error import InputError
from src.admin import admin_userpermission_change_v1
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1
from src.channel import channel_messages_v1, channel_details_v1, channel_join_v1, channel_leave_v1, \
    channel_invite_v1, channel_addowner_v1, channel_removeowner_v1
from src.channels import channels_create_v1, channels_listall_v1, channels_list_v1
from src.other import check_valid_token, clear_v1,return_token
from src.data_store import data_store
from src.message import message_send_v1,message_remove_v1,message_edit_v1,message_send_dm_v1
from src.user import user_profile_v1
from src.users import users_all_v1
from src.dm import dm_create_v1, dm_list_v1, dm_details_v1, dm_leave_v1, dm_remove_v1
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

# Admin Routes
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def post_admin_userpermission_change_v1():
    request_data = request.get_json()
    token = request_data['token']
    u_id = request_data['u_id']
    permission_id = request_data['permission_id']
    decoded_token = check_valid_token(token)
    return dumps(admin_userpermission_change_v1(decoded_token['auth_user_id'], u_id, permission_id))

# Auth Routes

# Registers a new user from given JSON data in Body
@APP.route("/auth/register/v2", methods=['POST'])
def post_auth_register():
    '''
    Given a registered user's email and password, returns their `token` value.

    Arguments:
        email (string)      - Unique email
        password (string)   - Password relevant to email/password combination
        name_first (string) - First name of user.
        name_last (string)  - Last name of user

    Exceptions:
        Input Error:
        - Email entered is not a valid email. 
        - Email address is already being used by another user.
        - Length of password is less than 6 characters.
        - Length of name_first is not between 1 and 50 characters inclusive.
        - Length of name_last is not between 1 and 50 characters inclusive.

    Return Value:
    {   
        token (string),      - Unique encrypted concat of auth_user_id and session_id
        auth_user_id (int)  - Unique authenticated Id of User.
    }
    '''
    request_data = request.get_json()
    print(request_data)
    auth_result = auth_register_v1(
        request_data['email'],
        request_data['password'],
        request_data['name_first'],
        request_data['name_last']
    )
    auth_user_id = auth_result['auth_user_id']
    token = return_token(auth_user_id)
    data_store.save()
    return dumps({
        'token':token,
        'auth_user_id' : auth_user_id
    })

# Login an account through a post request
@APP.route("/auth/login/v2", methods=['POST'])
def post_auth_login():
    '''
    Given a registered user's email and password, returns their `token` value.

    Arguments:
        email (string)   - Unique email
        password (string) - Password relevant to email/password combination

    Exceptions:
        Input Error:
        - email entered does not belong to a user
        - password is not correct

    Return Value:
    {   
        token (string),      - Unique encrypted concat of auth_user_id and session_id
        auth_user_id (int)  - Unique authenticated Id of User.
    }
    '''

    request_data = request.get_json()
    auth_result = auth_login_v1(
        request_data['email'],
        request_data['password']
    )
    auth_user_id = auth_result['auth_user_id']
    token = return_token(auth_user_id)
    data_store.save()
    return dumps({
        'token':token,
        'auth_user_id' : auth_user_id
    })

#logout an account through a post request
@APP.route("/auth/logout/v1", methods=['POST'])
def post_auth_logout():
    '''
    Given an active token, invalidates the token to log the user out.
    Does this by removing session id from user sessions list for user specified.
    Arguments:
        token (string)   - Unique encrypted concat of auth_user_id and session_id


    Exceptions:
        Access Error:
        - Thrown when the token passed in is invalid

    Return Value:
        {}
    '''
    request_data = request.get_json()
    _ = check_valid_token(request_data['token'])
    _ = auth_logout_v1(
        request_data['token']
    )
    data_store.save()
    return dumps({})

# Channel Routes

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    channel_details = channel_details_v1(token, channel_id)
    return dumps(channel_details)

@APP.route("/channel/messages/v2", methods=['GET'])
def get_channel_messages():
    '''
    Given a channel with ID channel_id that the authorised user
    is a member of, return up to 50 messages between index "start" 
    and "start + 50". Message with index 0 is the most recent message 
    in the channel. This function returns a new index "end" which is 
    the value of "start + 50", or, if this function has returned the 
    least recent messages in the channel, returns -1 in "end" to indicate 
    there are no more messages to load after this return.

    Arguments:
        token (string)   - Unique encrypted concat of auth_user_id and session_id
        channel_id (int) - Unique ID of Channel
        start (int)      - Start Index of Message

    Exceptions:
        Input Error:
        - channel_id does not refer to a valid channel
        - start is greater than the total number of messages in the channel
        Access Error:
        - channel_id is valid and the authorised user is not a member of the channel
        - Thrown when the token passed in is invalid


    Return Value:
    {   
        messages (list of strings) - on Successful completion.
        start    (int) - Start Index of Message
        end      (int) - End index of Message either start + 50 or -1
    }
    '''
    token = request.args.get('token')
    decoded_token = check_valid_token(token)
    channel_id = request.args.get('channel_id')
    start = request.args.get('start')
    channel_messages = channel_messages_v1(
        decoded_token['auth_user_id'],
        channel_id,
        start
    )
    data_store.save()
    return dumps(channel_messages)

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    decoded_token = check_valid_token(token)
    return dumps(channel_join_v1(decoded_token['auth_user_id'], channel_id))

@APP.route("/channel/leave/v1", methods=['POST'])
def post_channel_leave_v1():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    return dumps(channel_leave_v1(token, channel_id))

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    decoded_token = check_valid_token(token)
    return dumps(channel_invite_v1(decoded_token['auth_user_id'], channel_id, u_id))

@APP.route("/channel/addowner/v1", methods=['POST'])
def post_channel_addowner_v1():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    return dumps(channel_addowner_v1(token, channel_id, u_id))

@APP.route("/channel/removeowner/v1", methods=['POST'])
def post_channel_removeowner_v1():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    return dumps(channel_removeowner_v1(token, channel_id, u_id))

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
def channels_listall_v2():
    token = request.args.get('token')
    channels = channels_listall_v1(token)
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
    '''
    Send a message from the authorised user to the 
    channel specified by channel_id. Note: Each message 
    should have its own unique ID, i.e. no messages should 
    share an ID with another message, even if that other 
    message is in a different channel.
    Arguments:
        token (string)   - Unique encrypted concat of auth_user_id and session_id
        channel_id (int) - Unique ID of Channel
        message (string) - Message that will be sent to channel.

    Exceptions:
        Input Error:
        - channel_id does not refer to a valid channel
        - length of message is less than 1 or over 1000 characters
        Access Error:
        - channel_id is valid and the authorised user is not a member of the channel
        - Thrown when the token passed in is invalid


    Return Value:
    {   
        message_id (int) - Unique message_Id in the unique channel.
    }
    '''
    request_data = request.get_json()
    decoded_token = check_valid_token(request_data['token'])
    message_id = message_send_v1(
        decoded_token['auth_user_id'],
        request_data['channel_id'],
        request_data['message']
    )
    data_store.save()
    return dumps(message_id)

# Message Routes
@APP.route("/message/senddm/v1", methods=['POST'])
def post_message_dm_send():
    '''
    Send a message from authorised_user to the DM specified by dm_id. 
    Note: Each message should have it's own unique ID, i.e. no messages 
    should share an ID with another message, even if that other message 
    is in a different channel or DM.

    Arguments:
        token (string)      - Unique encrypted concat of auth_user_id and session_id
        dm_id (int)         - Unique ID of dm
        message (string)    - Message that will be sent to channel.

    Exceptions:
        Input Error:
        - dm_id does not refer to a valid channel
        - length of message is less than 1 or over 1000 characters
        Access Error:
        - dm_id is valid and the authorised user is not a member of the channel
        - Thrown when the token passed in is invalid


    Return Value:
    {   
        message_id (int) - Unique message_id in the unique dm.
    }
    '''
    request_data = request.get_json()
    decoded_token = check_valid_token(request_data['token'])
    message_id = message_send_dm_v1(
        decoded_token['auth_user_id'],
        request_data['dm_id'],
        request_data['message']
    )
    data_store.save()
    return dumps(message_id)

@APP.route("/message/edit/v1", methods=['PUT'])
def put_message_edit():
    request_data = request.get_json()
    _ = message_edit_v1(
        request_data['token'],
        request_data['message_id'],
        request_data['message']
        )
    data_store.save()
    return dumps({})

@APP.route("/message/remove/v1", methods=['DELETE'])
def delete_message_remove():
    request_data = request.get_json()
    _ = message_remove_v1(
        request_data['token'],
        request_data['message_id'],
        )
    data_store.save()
    return dumps({})
# Dm Routes
@APP.route("/dm/create/v1", methods=['POST'])
def dm_create_v1_post():
    request_data = request.get_json()
    token = request_data['token']
    u_ids = request_data['u_ids']
    decoded_token = check_valid_token(token)
    return dumps(dm_create_v1(decoded_token['auth_user_id'],u_ids))

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list_v1_get():
    token = request.args.get('token')
    decoded_token = check_valid_token(token)
    return dumps(dm_list_v1(decoded_token['auth_user_id']))

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details_v1_get():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    decoded_token = check_valid_token(token)
    return dumps(dm_details_v1(decoded_token['auth_user_id'], dm_id))

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave_v1_post():
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    decoded_token = check_valid_token(token)
    return dumps(dm_leave_v1(decoded_token['auth_user_id'], dm_id))

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove_delete():
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    decoded_token = check_valid_token(token)
    return dumps(dm_remove_v1(decoded_token['auth_user_id'], dm_id))
    
# User Routes
@APP.route("/user/profile/v1", methods=['get'])
def user_profile_v1_get():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    decoded_token = check_valid_token(token)
    return dumps(user_profile_v1(decoded_token['auth_user_id'], u_id))

# Users Routes
@APP.route("/users/all/v1", methods=['get'])
def users_all_v1_get():
    token = request.args.get('token')
    decoded_token = check_valid_token(token)
    return dumps(users_all_v1(decoded_token['auth_user_id']))

# Other routes
@APP.route("/get_data", methods=['GET'])
def get_all_data():
    '''
    Returns latest memory state of data_store object.

    Arguments:
        None

    Exceptions:
        None

    Return Value:
        data_store (dict)
    '''
    return dumps(data_store.get())

# Reset database through clearing the dictionaries
@APP.route("/clear/v1", methods=['DELETE'])
def delete_clear():
    '''
    Returns latest memory state of data_store object.

    Arguments:
        None

    Exceptions:
        None

    Return Value:
        {}
    '''
    clear_v1()
    return dumps({})

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)
    APP.run(port=config.port)
