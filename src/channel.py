from src.data_store import data_store
from src.error import InputError, AccessError

def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

# Check if the channel with channel_id is valid
def is_channel_valid(channel_id):

    channel_valid = False
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if channel_id in chan['id']:
            channel_valid = True

    return channel_valid

# Checks if user with auth_user_id is in channel with channel_id
def is_user_authorised(auth_user_id, channel_id):
    is_authorised = False
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if auth_user_id in chan['all_members']:
            is_authorised = True

    return is_authorised

# Returns the name of the channel with channel_id
def get_channel_name(channel_id):
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['name']

# Checks if channel with channel_id is public or private
def is_channel_public(channel_id):
    store = data_store.get()
    channel_store = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['is_public']

# Returns the auth_user_id of the channel owner with ID channel_id
def get_channel_owner(channel_id):
    store = data_store.get()
    channels = store['channels']

    for chan in channel_store:
        if chan['id'] == channel_id:
            return chan['owner_members'][0]

# Reurns a list containing details of the owner members
def user_details(auth_user_id):
    user_details_list = []
    store = data_store.get()
    user_store = store['users']

    for user in user_store:
        if user['u_id'] == auth_user_id:
            user_details_list.append(user)
    return user_details_list

# Given a channel with ID channel_id that the authorised user is a member of,
# provides basic details about the channel.
def channel_details_v1(auth_user_id, channel_id):

    # channel_id does not refer to a valid channel
    if not is_channel_valid(channel_id):
        raise InputError

    # channel_id is valid and the authorised user is not a member of the channel
    if not is_user_authorised(auth_user_id, channel_id):
        raise AccessError

    channel_owner_id = get_channel_owner(channel_id)

    # Return channel details
    return {
        'name': get_channel_name(channel_id),
        'is_public': is_channel_public(channel_id),
        'owner_members': user_details(channel_owner_id),
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

def channel_join_v1(auth_user_id, channel_id):
    return {
    }
