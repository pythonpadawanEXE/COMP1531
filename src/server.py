import sys
import signal
import pickle
from json import dumps
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask import Flask, request, send_from_directory
from src import config
from src.admin import admin_userpermission_change_v1, admin_user_remove_v1
from src.auth import auth_register_v1, auth_login_v1, auth_logout_v1,auth_password_reset_request,\
    auth_password_reset
from src.channel import channel_messages_v1, channel_details_v1, channel_join_v1, channel_leave_v1, \
    channel_invite_v1, channel_addowner_v1, channel_removeowner_v1
from src.channels import channels_create_v1, channels_listall_v1, channels_list_v1
from src.other import check_valid_token, clear_v1,return_token
from src.data_store import data_store
from src.message import message_pin, message_react, message_send_v1,message_remove_v1,message_edit_v1,message_send_dm_v1,\
        message_unpin, message_unreact, message_share, message_search
from src.standup import standup_active_v1, standup_send_v1, standup_start_v1
from src.user import user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1, \
                    notifications_get, user_stats_v1, user_profile_uploadphoto_v1
from src.users import users_all_v1, users_stats_v1
from src.dm import dm_create_v1, dm_list_v1, dm_details_v1, dm_leave_v1, dm_remove_v1, dm_messages_v1

try:
    store = pickle.load(open("datastore.p", "rb"))
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

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def delete_admin_user_remove_v1():
    request_data = request.get_json()
    token = request_data['token']
    u_id = request_data['u_id']
    decoded_token = check_valid_token(token)
    return dumps(admin_user_remove_v1(decoded_token['auth_user_id'], u_id))
    
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def post_admin_userpermission_change_v1():
    request_data = request.get_json()
    token = request_data['token']
    u_id = request_data['u_id']
    permission_id = request_data['permission_id']
    decoded_token = check_valid_token(token)
    return dumps(admin_userpermission_change_v1(decoded_token['auth_user_id'], u_id, permission_id))

# Auth Routes

@APP.route("/auth/register/v2", methods=['POST'])
def post_auth_register():
    request_data = request.get_json()
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

@APP.route("/auth/login/v2", methods=['POST'])
def post_auth_login():
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

@APP.route("/auth/logout/v1", methods=['POST'])
def post_auth_logout():
    request_data = request.get_json()
    _ = check_valid_token(request_data['token'])
    _ = auth_logout_v1(
        request_data['token']
    )
    data_store.save()
    return dumps({})

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def post_auth_password_reset_request():
    request_data = request.get_json()
    auth_password_reset_request(request_data['email'])
    
    data_store.save()
    return dumps({})

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def post_auth_password_reset():
    request_data = request.get_json()
    auth_password_reset(request_data['reset_code'],request_data['new_password'])
    
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

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2():
    token = request.args.get('token')
    channels = channels_listall_v1(token)
    return dumps(channels)

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    token = request.args.get('token')
    decoded_token = check_valid_token(token)
    return dumps(channels_list_v1(decoded_token['auth_user_id']))

# Message routes

@APP.route("/message/send/v1", methods=['POST'])
def post_message_send():
    request_data = request.get_json()
    decoded_token = check_valid_token(request_data['token'])
    message_id = message_send_v1(
        decoded_token['auth_user_id'],
        request_data['channel_id'],
        request_data['message']
    )
    data_store.save()
    return dumps(message_id)

@APP.route("/message/senddm/v1", methods=['POST'])
def post_message_dm_send():
    request_data = request.get_json()
    decoded_token = check_valid_token(request_data['token'])
    message_id = message_send_dm_v1(
        decoded_token['auth_user_id'],
        request_data['dm_id'],
        request_data['message']
    )
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

@APP.route("/message/react/v1", methods=['POST'])
def message_react_v1_post():
    request_data = request.get_json()
    token = request_data['token']
    message_id = int(request_data['message_id'])
    react_id = int(request_data['react_id'])
    decoded_token = check_valid_token(token)
    return(dumps(message_react(decoded_token['auth_user_id'], message_id, react_id)))

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin_v1_post():
    request_data = request.get_json()
    decoded_token = check_valid_token(request_data['token'])
    _ = message_pin(
        decoded_token['auth_user_id'],
        request_data['message_id']

    )

    data_store.save()
    return dumps({})

@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin_v1_post():
    request_data = request.get_json()
    decoded_token = check_valid_token(request_data['token'])
    _ = message_unpin(
        decoded_token['auth_user_id'],
        request_data['message_id']

    )

    data_store.save()
    return dumps({})
@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact_v1():
    request_data = request.get_json()
    token = request_data['token']
    message_id = int(request_data['message_id'])
    react_id = int(request_data['react_id'])
    
    return(dumps(message_unreact(token, message_id, react_id)))

@APP.route("/message/share/v1", methods=['POST'])
def message_share_v1():
    request_data = request.get_json()
    token = request_data['token']
    og_message_id = int(request_data['og_message_id'])
    message = request_data['message']
    channel_id = int(request_data['channel_id'])
    dm_id = int(request_data['dm_id'])
    
    return(dumps(message_share(token, og_message_id, channel_id, dm_id, message)))

@APP.route("/search/v1", methods=['GET'])
def search_v1():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return dumps(message_search(token, query_str))

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

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages_get():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))
    decoded_token = check_valid_token(token)
    dm_messages = dm_messages_v1(
        decoded_token['auth_user_id'],
        dm_id,
        start
    )
    return jsonify(dm_messages)

# User Routes

@APP.route("/user/profile/v1", methods=['GET'])
def user_profile_v1_get():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    decoded_token = check_valid_token(token)
    return dumps(user_profile_v1(decoded_token['auth_user_id'], u_id))

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def put_user_profile_setname_v1():
    request_data = request.get_json()
    token = request_data['token']
    name_first = request_data['name_first']
    name_last = request_data['name_last']
    return dumps(user_profile_setname_v1(token, name_first, name_last))

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def put_user_profile_setemail_v1():
    request_data = request.get_json()
    token = request_data['token']
    email = request_data['email']
    return dumps(user_profile_setemail_v1(token, email))

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def put_user_profile_sethandle_v1():
    request_data = request.get_json()
    token = request_data['token']
    handle_str = request_data['handle_str']
    return dumps(user_profile_sethandle_v1(token, handle_str))

@APP.route("/notifications/get/v1", methods=['GET'])
def notifications_get_v1():
    token = request.args.get('token')
    return dumps(notifications_get(token))

@APP.route("/user/stats/v1", methods=['GET'])
def user_stats_v1_get():
    token = request.args.get('token')
    return jsonify(user_stats_v1(token))

# user_profile_uploadphoto_v1
@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_uploadphoto_v1_post():
    request_data = request.get_json()
    token = request_data['token']
    img_url = request_data['img_url']
    x_start = int(request_data['x_start'])
    y_start = int(request_data['y_start'])
    x_end = int(request_data['x_end'])
    y_end = int(request_data['y_end'])

    return dumps(user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end))

@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('', path)

# Users Routes

@APP.route("/users/all/v1", methods=['GET'])
def users_all_v1_get():
    token = request.args.get('token')
    _ = check_valid_token(token)
    return dumps(users_all_v1())

@APP.route("/users/stats/v1", methods=['GET'])
def users_stats_v1_get():
    token = request.args.get('token')
    return jsonify(users_stats_v1(token))

# Standup routes

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start_v1_post():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = int(request_data['channel_id'])
    length = int(request_data['length'])
    decoded_token = check_valid_token(token)
    return dumps(standup_start_v1(decoded_token['auth_user_id'], channel_id, length))

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active_v1_get():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    decoded_token = check_valid_token(token)
    return dumps(standup_active_v1(decoded_token['auth_user_id'], channel_id))

@APP.route("/standup/send/v1", methods=['POST'])
def standup_send_v1_post():
    request_data = request.get_json()
    token = request_data['token']
    channel_id = int(request_data['channel_id'])
    message = request_data['message']
    decoded_token = check_valid_token(token)
    return dumps(standup_send_v1(decoded_token['auth_user_id'], channel_id, message))

# Other routes

@APP.route("/get_data", methods=['GET'])
def get_data():
    return dumps(data_store.get())

@APP.route("/clear/v1", methods=['DELETE'])
def clear_all_data():
    return dumps(clear_v1())

#### NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)
    APP.run(port=config.port)
