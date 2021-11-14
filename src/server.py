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
        message_unpin, message_unreact, message_share, message_search, message_sendlater, message_sendlaterdm_v1
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
    """ Given a user by their u_id, remove them from the Streams. 
    
        Arguments:
            auth_user_id (int)    - The user ID of the user who is calling remove.
            u_id (int)            - The user ID of the user who is being removed.

        Exceptions:
            InputError  - u_id does not refer to a valid user,
                        - u_id refers to a user who is the only global owner,

            AccessError - the authorised user is not a global owner,

        Return Value:
            Returns { } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    u_id = request_data['u_id']
    decoded_token = check_valid_token(token)
    return dumps(admin_user_remove_v1(decoded_token['auth_user_id'], u_id))
    
@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def post_admin_userpermission_change_v1():
    """ Given a user by their user ID, set their permissions to new permissions described by permission_id.
    
        Arguments:
            auth_user_id (int)    - The user ID of the user who is changing the permissions.
            u_id (int)            - The user ID of the user who's permissions are being changed.
            permission_id         - The permission id (1 or 2) the user will have.

        Exceptions:
            InputError  - u_id does not refer to a valid user.
                        - u_id refers to a user who is the only global owner and they are being demoted to a user.
                        - permission_id is invalid.

            AccessError - the authorised user is not a global owner

        Return Value:
            Returns { } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    u_id = request_data['u_id']
    permission_id = request_data['permission_id']
    decoded_token = check_valid_token(token)
    return dumps(admin_userpermission_change_v1(decoded_token['auth_user_id'], u_id, permission_id))

# Auth Routes

@APP.route("/auth/register/v2", methods=['POST'])
def post_auth_register():
    """ Create a unique user dictionary in the users data store with
        the provided inputs and creates a unique handle and id and creates a password
        in the passwords dictionary. Makes a session.

    Arguments:
        email (string)        - The email of the user to be registered.
        password (string)     - The password of the user to be registered.
        name_first (string)   - The first name of the user to be registered.
        name_last (string)    - The last name of the user to be registered.

    Exceptions:
        InputError  - Occurs when email input is invalid or duplicated,
                    - Occurs when  length of password is less than 6 characters  or invalid.
                    - Occurs when length of name_first or name_last is less than 1 character
                    or greater than or equal to 50 characters

    Return Values:
        { auth_user_id (int),
          token        (string),
         }                          - Upon successful completion.
        
    """
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
    """ Checks if valid email password combination and returns auth_user_id.

    Arguments:
        email (string)        - The email of the user to be registered.
        password (string)     - The password of the user to be registered.


    Exceptions:
        InputError  - Occurs when email input is invalid or doesn't belong to a user.
                    - Occurs when length of password is invalid or does not match the
                      password email combination.

    Return Value:
        { auth_user_id (int),
         }                          - Upon successful completion.
        
    """
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
    """ Given a token deocdes the token and removes the session_id assosciated with that token from the database.

    Arguments:
        token (string)        - The encoded token an amlagamation of auth_user_id and session_id

    Exceptions:
        AcessError
        -invalid token

    Return Values:
        { session_id (int)     - Upon successful completion  of old session_id now invalid.
          
         }                         
        
    """
    request_data = request.get_json()
    _ = check_valid_token(request_data['token'])
    _ = auth_logout_v1(
        request_data['token']
    )
    data_store.save()
    return dumps({})

@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def post_auth_password_reset_request():
    """ 
    Given an email address, if the user is a registered user, 
    sends them an email containing a specific secret code, that when 
    entered in auth/passwordreset/reset, shows that the user trying to reset 
    the password is the one who got sent this email. No error should be raised 
    when passed an invalid email, as that would pose a security/privacy concern. 
    When a user requests a password reset, they should be logged out of all current 
    sessions.

    Arguments:
        email (string)        - The email of the user who is requesting a password reset


    Return Values:
        {}                      
        
    """
    request_data = request.get_json()
    auth_password_reset_request(request_data['email'])
    
    data_store.save()
    return dumps({})

@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def post_auth_password_reset():
    """ 
    Given a reset code for a user, set that user's new password to the password provided.

    Arguments:
        reset_code (string)        - The reset_code of the user who is requesting a password reset
                                        received via email.
        
        new_password (string)      -The password that will replace the old password.


    Return Values:
        {}                      
        
    """
    request_data = request.get_json()
    auth_password_reset(request_data['reset_code'],request_data['new_password'])
    
    data_store.save()
    return dumps({})

# Channel Routes

@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    """ Given a channel with ID channel_id that the authorised user is a member of, provide basic
        details about the channel.

        Arguments:
            token (str)           - Token of the user who is a member of the channel.
            channel_id (int)      - Channel ID of the channel the user is a member of.

        Exceptions:
            InputError  - Occurs when channel_id does not refer to a valid channel.

            AccessError - Occurs when channel_id is valid and the authorised user is
            not a member of the channel.

        Return Value:
            Returns { name, is_public, owner_members, all_members } on successful completion.
    """
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    channel_details = channel_details_v1(token, channel_id)
    return dumps(channel_details)

@APP.route("/channel/messages/v2", methods=['GET'])
def get_channel_messages():
    """ Returns the 50 most recent messages from start.

        Arguments:
            auth_user_id (int)      - User ID of the user who is a member of the channel.
            channel_id (int)        - Channel ID of the channel the user is a member of.
            start (int)             - Starting index of messages to be displayed.

        Exceptions:
            InputError  - Occurs when channel_id does not refer to a valid channel or
                          start is greater than the total number of messages in the channel.

            AccessError - Occurs when channel_id is valid and the authorised user is not a
            member of the channel.

        Return Value:
            Returns { messages, start, end } on successful completion
    """
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
    """ Given a channel_id of a channel that the authorised user can join, adds
        them to that channel.

        Arguments:
            auth_user_id (int)      - User ID of the user who is being added to the channel.
            channel_id (int)        - Channel ID of the channel that is used to join a user to.

        Exceptions:
            InputError  - Occurs when channel_id does not refer to a valid channel or
                          the authorised user is already a member of the channel.

            AccessError - Occurs when channel_id refers to a channel that is private
                          and the authorised user is not already a channel member and
                          is not a global owner.

        Return Value:
            Returns { } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    decoded_token = check_valid_token(token)
    return dumps(channel_join_v1(decoded_token['auth_user_id'], channel_id))

@APP.route("/channel/leave/v1", methods=['POST'])
def post_channel_leave_v1():
    """ Given a channel with ID channel_id that the authorised user is a member of,
    remove them as a member of the channel. Their messages should remain in the channel.
    If the only channel owner leaves, the channel will remain.

        Arguments:
            token (str)           - Token of the user who is a member of the channel.
            channel_id (int)      - Channel ID of the channel the user is a member of.

        Exceptions:
            InputError  - Occurs when channel_id does not refer to a valid channel.

            AccessError - Occurs when channel_id is valid and the authorised user is
            not a member of the channel.

        Return Value:
            Returns { } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    return dumps(channel_leave_v1(token, channel_id))

@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2():
    """ 
        Invites a user with ID u_id to join a channel with ID channel_id. 
        Once invited, the user is added to the channel immediately. 
        In both public and private channels, all members are able to invite users.
        Arguments:
            auth_user_id (int)    - The user ID of the user who is inviting u_id.
            channel_id (int)      - The channel ID that user u_id is being invited to.
            u_id (int)            - The user ID of the user who is being invited.

        Exceptions:
            InputError  - Occurs when channel_id does not refer to a valid channel or
                          u_id does not refer to a valid user or
                          u_id refers to a user who is already a member of the channel.

            AccessError - Occurs when channel_id is valid and the authorised user
                          is not a member of the channel.

        Return Value:
            Returns { } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    decoded_token = check_valid_token(token)
    return dumps(channel_invite_v1(decoded_token['auth_user_id'], channel_id, u_id))

@APP.route("/channel/addowner/v1", methods=['POST'])
def post_channel_addowner_v1():
    """ Make user with user id u_id an owner of the channel.

        Arguments:
            token (str)           - Token of the user who is the owner of the channel.
            channel_id (int)      - Channel ID of the channel of the authorised owner user.
            u_id (int)            - User ID of the user who is being promoted to owner.

        Exceptions:
            InputError  - Occurs when channel_id does not refer to a valid channel.
                          Occurs when u_id does not refer to a valid user.
                          Occurs when u_id refers to a user who is not a member of the channel.
                          Occurs when u_id refers to a user who is already an owner of the channel.

            AccessError - Occurs when channel_id is valid and the authorised user does not have owner
            permissions in the channel.

        Return Value:
            Returns { } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    return dumps(channel_addowner_v1(token, channel_id, u_id))

@APP.route("/channel/removeowner/v1", methods=['POST'])
def post_channel_removeowner_v1():
    """ Remove user with user id u_id as an owner of the channel.

        Arguments:
            token (str)           - Token of the user who is the owner of the channel.
            channel_id (int)      - Channel ID of the channel of the authorised owner user.
            u_id (int)            - User ID of the user who is being removed from owner.

        Exceptions:
            InputError  - Occurs when channel_id does not refer to a valid channel.
                          Occurs when u_id does not refer to a valid user.
                          Occurs when u_id refers to a user who is not an owner of the channel.
                          Occurs when u_id refers to a user who is currently the only owner of the channel.

            AccessError - Occurs when channel_id is valid and the authorised user does not have owner
            permissions in the channel.

        Return Value:
            Returns { } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    u_id = request_data['u_id']
    return dumps(channel_removeowner_v1(token, channel_id, u_id))

# Channels Routes

@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    """ Creates a channel as specified by the parameters.

    Arguments:
        auth_user_id (int)    - The user id of the calling user.
        name (string)         - The name of the channel to be created.
        is_public (boolean)   - Determines whether the channel is public
        ...

    Exceptions:
        InputError  - Occurs when length of name is less than 1 or more than 20 characters.
        AccessError - Occurs when the user's id does not exist in the data store.

    Return Value:
        Returns { channel_id } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    name = request_data['name']
    is_public = request_data['is_public'] == True
    decoded_token = check_valid_token(token)
    return dumps(channels_create_v1(decoded_token['auth_user_id'], name, is_public))

@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2():
    """ Lists all channels that exist including public and private channels.

        Arguments:
            token (int)    - The token of the user.

        Exceptions:
            AccessError - Occurs when the token is not valid.

        Return Value:
            Returns { channels } on successful completion.
    """
    token = request.args.get('token')
    channels = channels_listall_v1(token)
    return dumps(channels)

@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    """ Lists all channels that the given user id is a member of.

        Arguments:
            auth_user_id (int)    - The user id of the user whose channel membership
                                    is being listed.

        Exceptions:
            AccessError - Occurs when the user's id does not exist in the data store.

        Return Value:
            Returns { channels } on successful completion.
    """
    token = request.args.get('token')
    decoded_token = check_valid_token(token)
    return dumps(channels_list_v1(decoded_token['auth_user_id']))

# Message routes

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

@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater_v1():
    '''
    Send a message from the authorised user to the channel specified by channel_id automatically at a specified time in the future
    Arguments:
        token (string)      - Token of user sending the message
        channel_id (int)    - Unique ID of channel
        message (string)    - Message user is sending
        time_sent (int)     - The time the user message is executed

    Exceptions:
        Input Error:
        - channel_id does not refer to a valid channel
        - length of message is less than 1 or over 1000 characters
        - time_sent is a time in the past

        Access Error:
        - channel_id is valid and the authorised user is not a member of the channel they are trying to post to

    Return Value:
        { message_id }
    '''
    request_data = request.get_json()
    token = request_data['token']
    channel_id = request_data['channel_id']
    message = request_data['message']
    time_sent = request_data['time_sent']
    return dumps(message_sendlater(token, channel_id, message, time_sent))

@APP.route("/message/senddm/v1", methods=['POST'])
def post_message_dm_send():
    '''
    Send a message from the authorised user to the 
    dm specified by dm_id. Note: Each message should have 
    its own unique ID, i.e. no messages should share an ID with another 
    message, even if that other message is in a different dm.

    Arguments:
        token (string)      - Unique encrypted concat of auth_user_id and session_id
        dm_id (int)         - Unique ID of dm
        message (string)    - Message that will be sent to channel.

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
    message_id = message_send_dm_v1(
        decoded_token['auth_user_id'],
        request_data['dm_id'],
        request_data['message']
    )
    return dumps(message_id)

@APP.route("/message/edit/v1", methods=['PUT'])
def put_message_edit():
    '''
    Given a message, update its text with new text. 
    If the new message is an empty string, the message is deleted.

    Arguments:
        token (string)      - Unique encrypted concat of auth_user_id and session_id
        message_id (int)    - Unique ID of message
        message (string)    - Message that will be sent to channel.

    Exceptions:
        Input Error:
        - message_id does not refer to a valid message
        - length of message is less than 1 or over 1000 characters
        Access Error:
        - the auth_user_id is neither the message creator nor has permissions as owner in the channel/dm
        - Thrown when the token passed in is invalid


    Return Value:
        {  }
    '''
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
    '''
    Given a message_id for a message, this message is removed from the channel/DM
    Arguments:
        token (string)      - Unique encrypted concat of auth_user_id and session_id
        message_id (int)    - Unique ID of message

    Exceptions:
        Input Error:
        - message_id does not refer to a valid message

        Access Error:
        - the auth_user_id is neither the message creator nor has permissions as owner in the channel/dm
        - Thrown when the token passed in is invalid


    Return Value:
        { }
    '''
    request_data = request.get_json()
    _ = message_remove_v1(
        request_data['token'],
        request_data['message_id'],
        )
    data_store.save()
    return dumps({})

@APP.route("/message/react/v1", methods=['POST'])
def message_react_v1_post():
    '''
    Given a message within a channel or DM the authorised user is part of, add a "react" to that particular message.
    Arguments:
        token (string)      - User who is attempting to react
        message_id (int)    - Unique ID of message
        react_id (int)      - Unique ID of react

    Exceptions:
        Input Error:
        - message_id is not a valid message within a channel or DM that the authorised user has joined
        - react_id is not a valid react ID
        - the message does not contain a react with ID react_id from the authorised user

    Return Value:
        { }
    '''
    request_data = request.get_json()
    token = request_data['token']
    message_id = int(request_data['message_id'])
    react_id = int(request_data['react_id'])
    decoded_token = check_valid_token(token)
    return(dumps(message_react(decoded_token['auth_user_id'], message_id, react_id)))

@APP.route("/message/pin/v1", methods=['POST'])
def message_pin_v1_post():
    '''
    Given a message within a channel or DM, mark it as "pinned"
    Arguments:
        token (string)      - User who is attempting to react
        message_id (int)    - Unique ID of message

    Exceptions:
        Input Error:
        - message_id is not a valid message within a channel or DM that the authorised user has joined
        - the message is already pinned
        Access Error:
        -message_id refers to a valid message in a joined channel/DM and the authorised user does not have 
        owner permissions in the channel/DM
        -invalid token

    Return Value:
        { }
    '''
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
    '''
    Given a message within a channel or DM, mark it as not "pinned"
    Arguments:
        token (string)      - User who is attempting to react
        message_id (int)    - Unique ID of message

    Exceptions:
        Input Error:
        - message_id is not a valid message within a channel or DM that the authorised user has joined
        - the message is already unpinned
        Access Error:
        -message_id refers to a valid message in a joined channel/DM and the authorised user does not have 
        owner permissions in the channel/DM
        -invalid token

    Return Value:
        { }
    '''
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
    '''
    Given a message within a channel or DM the authorised user is part of, remove a "react" to that particular message.
    Arguments:
        token (string)      - User who is attempting to react
        message_id (int)    - Unique ID of message
        react_id (int)      - Unique ID of react

    Exceptions:
        Input Error:
        - message_id is not a valid message within a channel or DM that the authorised user has joined
        - react_id is not a valid react ID
        - the message does not contain a react with ID react_id from the authorised user

    Return Value:
        { }
    '''
    request_data = request.get_json()
    token = request_data['token']
    message_id = int(request_data['message_id'])
    react_id = int(request_data['react_id'])
    
    return(dumps(message_unreact(token, message_id, react_id)))

@APP.route("/message/share/v1", methods=['POST'])
def message_share_v1():
    '''
    og_message_id is the ID of the original message. channel_id is the channel that the message
    is being shared to, and is -1 if it is being sent to a DM. dm_id is the DM that the message
    is being shared to, and is -1 if it is being sent to a channel. message is the optional message
    in addition to the shared message, and will be an empty string '' if no message is given. A
    new message should be sent to the channel/DM identified by the channel_id/dm_id that contains
    the contents of both the original message and the optional message. The format does not matter
    as long as both the original and optional message exist as a substring within the new message.
    Arguments:
        token (string)      - Token of the user who is trying to share the message
        og_message_id (int) - Unique ID of original message
        message (string)    - Optional message to be added to the shared message
        channel_id (int)    - Unique ID of channel
        dm_id (int)         - Unique ID of DM

    Exceptions:
        Input Error:
        - both channel_id and dm_id are invalid
        - neither channel_id nor dm_id are -1
        - og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
        - length of message is more than 1000 characters

        Access Error:
        - the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user 
          has not joined the channel or DM they are trying to share the message to

    Return Value:
        { shared_message_id }
    '''
    request_data = request.get_json()
    token = request_data['token']
    og_message_id = int(request_data['og_message_id'])
    message = request_data['message']
    channel_id = int(request_data['channel_id'])
    dm_id = int(request_data['dm_id'])
    
    return(dumps(message_share(token, og_message_id, channel_id, dm_id, message)))

@APP.route("/search/v1", methods=['GET'])
def search_v1():
    '''
    Given a query string, return a collection of messages in all of the channels/DMs that the user has joined that contain the query.
    Arguments:
        token (string)      - token of user we are searching messages for
        query_str  (string) - Message query to search for

    Exceptions:
        Input Error:
        - length of query_str is less than 1 or over 1000 characters

    Return Value:
        { messages }
    '''
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    return dumps(message_search(token, query_str))

@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm_v1_post():
    '''
    Send a message from the authorised user to the dm specified by dm_id automatically at a specified time in the future
    Arguments:
        token (string)      - Token of user sending the message
        dm_id (int)    - Unique ID of dm
        message (string)    - Message user is sending
        time_sent (int)     - The time the user message is executed

    Exceptions:
        Input Error:
        - dm_id does not refer to a valid dm
        - length of message is less than 1 or over 1000 characters
        - time_sent is a time in the past

        Access Error:
        - dm_id is valid and the authorised user is not a member of the dm they are trying to post to

    Return Value:
        { message_id }
    '''
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    message = request_data['message']
    time_sent = request_data['time_sent']
    return dumps(message_sendlaterdm_v1(token, dm_id, message, time_sent))

# Dm Routes

@APP.route("/dm/create/v1", methods=['POST'])
def dm_create_v1_post():
    ''' 
    Creates a dm as specified by the parameters.

    Arguments:
        auth_user_id (int)   - The user id of the calling user.
        u_ids (list)         - The u_id list of the member to be added in.
    
    Return Value:
        Returns { dm_id, name, owner, all members, messages } on successful completion.
    '''
    request_data = request.get_json()
    token = request_data['token']
    u_ids = request_data['u_ids']
    decoded_token = check_valid_token(token)
    return dumps(dm_create_v1(decoded_token['auth_user_id'],u_ids))

@APP.route("/dm/list/v1", methods=['GET'])
def dm_list_v1_get():
    ''' 
    Lists all dms that exist.

        Arguments:
        auth_user_id (int)    - The user id of the calling user.

        Return Value:
            Returns { dms } on successful completion.
    '''
    token = request.args.get('token')
    decoded_token = check_valid_token(token)
    return dumps(dm_list_v1(decoded_token['auth_user_id']))

@APP.route("/dm/details/v1", methods=['GET'])
def dm_details_v1_get():
    ''' 
    Given a dm with ID dm_id that the authorised user is a member of, provide basic
        details about the dm.

        Arguments:
            auth_user_id (int)  - authorised user id of the user who is a member of the dm.
            dm_id (int)         - Dm ID of the dm the user is a member of.

        Exceptions:
            InputError  - Occurs when dm_id does not refer to a valid dm.

            AccessError - Occurs when dm_id is valid and the authorised user is
                          not a member of the dm.

        Return Value:
            Returns { name, owner, all_members } on successful completion.
    '''
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    decoded_token = check_valid_token(token)
    return dumps(dm_details_v1(decoded_token['auth_user_id'], dm_id))

@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave_v1_post():
    '''
    Given a dm with ID dm_id that the authorised user is a member of,
    remove them as a member of the dm. Their messages should remain in the dm.
    If the only dm owner leaves, the dm will remain.

        Arguments:
            auth_user_id (int)      - authorised user id of the user who is a member of the dm.
            dm_id (int)             - Dm ID of the dm the user is a member of.

        Exceptions:
            InputError  - Occurs when dm_id does not refer to a valid dm.

            AccessError - Occurs when dm_id is valid and the authorised user is
                          not a member of the dm.

        Return Value:
            Returns { } on successful completion.
    '''
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    decoded_token = check_valid_token(token)
    return dumps(dm_leave_v1(decoded_token['auth_user_id'], dm_id))

@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove_delete():
    '''
    Given a dm with ID dm_id that the authorised user is a member of,
    removing an existing dm, so all members are no longer in the dm. This can only
    done by the original creator of the dm.

        Arguments:
            auth_user_id (int)      - authorised user id of the user who is a creator of the dm.
            dm_id (int)             - Dm ID of the dm the user is a member of.

        Exceptions:
            InputError  - Occurs when dm_id does not refer to a valid dm.

            AccessError - Occurs when dm_id is valid and the authorised user is
                          not the creator of the dm.

        Return Value:
            Returns { } on successful completion.
    '''
    request_data = request.get_json()
    token = request_data['token']
    dm_id = request_data['dm_id']
    decoded_token = check_valid_token(token)
    return dumps(dm_remove_v1(decoded_token['auth_user_id'], dm_id))

@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages_get():
    '''
    Given a dm with ID dm_id that the authorised user is a member of and and the 
    starting index of messages to be displayed from. Lists the 50 most recent 
    messages from start.

        Arguments:
            auth_user_id (int)      - User ID of the user who is a member of the dm.
            dm_id (int)             - Dm ID of the dm the user is a member of.
            start (int)             - Starting index of messages to be displayed.

        Exceptions:
            InputError  - Occurs when dm_id does not refer to a valid dm or
                          start is greater than the total number of messages in the dm.
                          or less that 0 which refers to a invalid Start Index.

            AccessError - Occurs when dm_id is valid and the authorised user is not a
                          member of the dm.

        Return Value:
            Returns { messages, start, end } on successful completion.
    '''
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
    """ For a valid user, returns information about their user_id, email, first name, last name, and handle
    
        Arguments:
            auth_user_id (int)    - The user ID of the user who is calling user_profile_v1.
            u_id (int)            - The user ID of the user who's profile is being sent.

        Exceptions:
            InputError  - u_id does not refer to a valid user,

            AccessError - the authorised user does not exist

        Return Value:
            Returns { user } on successful completion.
    """
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))
    decoded_token = check_valid_token(token)
    return dumps(user_profile_v1(decoded_token['auth_user_id'], u_id))

@APP.route("/user/profile/setname/v1", methods=['PUT'])
def put_user_profile_setname_v1():
    """ Update the authorised user's first and last name
    
        Arguments:
            token (string)        - The token of the user who is calling user_profile_setname_v1.
            name_first (string)   - The new first name for this user
            name_last (string)    - The new last name for this user

        Exceptions:
            InputError  - length of name_first is not between 1 and 50 characters inclusive
                        - length of name_last is not between 1 and 50 characters inclusive

            AccessError - the authorised user does not exist

        Return Value:
            Returns { } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    name_first = request_data['name_first']
    name_last = request_data['name_last']
    return dumps(user_profile_setname_v1(token, name_first, name_last))

@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def put_user_profile_setemail_v1():
    """ Update the authorised user's email address
    
        Arguments:
            token (string)        - The token of the user who is calling user_profile_setemail_v1.
            email (string)        - The new email the user wishes to use

        Exceptions:
            InputError  - email entered is not a valid email
                        - email address is already being used by another user

            AccessError - the authorised user does not exist

        Return Value:
            Returns { } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    email = request_data['email']
    return dumps(user_profile_setemail_v1(token, email))

@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def put_user_profile_sethandle_v1():
    """ Update the authorised user's handle (i.e. display name)
    
        Arguments:
            token (string)        - The token of the user who is calling user_profile_sethandle_v1.
            handle_str (string)   - The new email the user wishes to use

        Exceptions:
            InputError  - length of handle_str is not between 3 and 20 characters inclusive
                        - handle_str contains characters that are not alphanumeric
                        - the handle is already used by another user

            AccessError - the authorised user does not exist

        Return Value:
            Returns { } on successful completion.
    """
    request_data = request.get_json()
    token = request_data['token']
    handle_str = request_data['handle_str']
    return dumps(user_profile_sethandle_v1(token, handle_str))

@APP.route("/notifications/get/v1", methods=['GET'])
def notifications_get_v1():
    """ Return the user's most recent 20 notifications, ordered from most recent to least recent.
    
        Arguments:
            token (string)  - The token of the user who is calling notifications_get_v1.

        Exceptions:
            AccessError     - the authorised user does not exist

        Return Value:
            Returns { notifications } on successful completion.
    """
    token = request.args.get('token')
    return dumps(notifications_get(token))

@APP.route("/user/stats/v1", methods=['GET'])
def user_stats_v1_get():
    """
    Fetches the required statistics about this user's use of UNSW Streams.
    Arguments:
        token (string)  - The token of the user who is calling notifications_get_v1.

    Exception:
        AccessError
        - Invalid token
    Return Value:
            Returns { user_stats } on successful completion.    
    """
    token = request.args.get('token')
    return jsonify(user_stats_v1(token))

# user_profile_uploadphoto_v1
@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_profile_uploadphoto_v1_post():
    """ For a valid user, returns information about their user_id, email, first name, last name, and handle
    
        Arguments:
            auth_user_id (int)    - The user ID of the user who is calling user_profile_v1.
            u_id (int)            - The user ID of the user who's profile is being sent.

        Exceptions:
            InputError  - u_id does not refer to a valid user,

            AccessError - the authorised user does not exist

        Return Value:
            Returns { user } on successful completion.
    """
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
    """ Returns a list of all users and their associated details.

        Return Value:
            Returns { users } on successful completion.
    """
    token = request.args.get('token')
    _ = check_valid_token(token)
    return dumps(users_all_v1())

@APP.route("/users/stats/v1", methods=['GET'])
def users_stats_v1_get():
    """
    Fetches the required statistics about the use of UNSW Streams.
    Arguments:
        token (string)  - The token of the user who is calling notifications_get_v1.

    Exception:
        AccessError
        - Invalid token
    Return Value:
            Returns { workspace_stats } on successful completion.    
    """
    token = request.args.get('token')
    return jsonify(users_stats_v1(token))

# Standup routes

@APP.route("/standup/start/v1", methods=['POST'])
def standup_start_v1_post():
    """
    For a given channel, start the standup period whereby for the next "length" 
    seconds if someone calls "standup/send" with a message, it is buffered during 
    the X second window then at the end of the X second window a message will be 
    added to the message queue in the channel from the user who started the standup. 
    "length" is an integer that denotes the number of seconds that the standup occurs for.

    Arguments:
        token (string) - Token of the user who is making the standup.
        channel_id (int)    - channel_id of channel to contain standup
        length  (int)       - delay of standup in seconds

    Exceptions:

        AccessError:
        -invalid token
        - channel_id is valid and the authorised user is not a member of the channel
        
        InputError:
        -channel_id does not refer to a valid channel
        -length is a negative integer
        -an active standup is currently running in the channel

    Return
        {time_finish } on successful completion
    """
    request_data = request.get_json()
    token = request_data['token']
    channel_id = int(request_data['channel_id'])
    length = int(request_data['length'])
    decoded_token = check_valid_token(token)
    return dumps(standup_start_v1(decoded_token['auth_user_id'], channel_id, length))

@APP.route("/standup/active/v1", methods=['GET'])
def standup_active_v1_get():
    """
    For a given channel, return whether a standup is active in it, 
    and what time the standup finishes. If no standup is active, 
    then time_finish returns None.

    Arguments:
        token (string) - Token of the user who is making the standup.
        channel_id (int)    - channel_id of channel to contain standup

    Exceptions:

        AccessError:
        -invalid token
        - channel_id is valid and the authorised user is not a member of the channel
        
        InputError:
        -channel_id does not refer to a valid channel
        

    Return
        {is_active, time_finish} on successful completion
    """
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    decoded_token = check_valid_token(token)
    return dumps(standup_active_v1(decoded_token['auth_user_id'], channel_id))

@APP.route("/standup/send/v1", methods=['POST'])
def standup_send_v1_post():
    """
    Sending a message to get buffered in the standup queue, 
    assuming a standup is currently active. Note: We do not 
    expect @ tags to be parsed as proper tags when sending to 
    standup/send

    Arguments:
        token (string) - Token of the user who is making the standup.
        channel_id (int)    - channel_id of channel to contain standup
        message (dict)        -  message contents

    Exceptions:

        AccessError:
        -invalid token
        - channel_id is valid and the authorised user is not a member of the channel
        
        InputError:
        -channel_id does not refer to a valid channel
        -length of message is over 1000 characters
        -an active standup is currently running in the channel

    Return
        {} on successful completion
    """
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
