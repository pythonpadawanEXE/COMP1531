"""
channels.py

This module handles the creation and listing of channels for Streams.

Functions:
    channels_list_v1(auth_user_id) -> { channels }
    channels_listall_v1(auth_user_id) -> { channels }
    channels_create_v1(auth_user_id, name, is_public) -> { channel_id }
"""

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import verify_user_id

def channels_list_v1(auth_user_id):
    """ Lists all channels that the given user id is a member of.

        Arguments:
            auth_user_id (int)    - The user id of the user whose channel membership
                                    is being listed.

        Exceptions:
            AccessError - Occurs when the user's id does not exist in the data store.

        Return Value:
            Returns { channels } on successful completion.
    """

    # Verifies that the user exists in the data store, raises an AccessError otherwise.
    if not verify_user_id(auth_user_id):
        raise AccessError

    # Iterates through the list of channels and
    # returns the subset that the given user is a member of.
    store = data_store.get()
    channel_store = store['channels']
    channels = []
    for chan in channel_store:
        if auth_user_id in chan['all_members']:
            channels.append({'channel_id' : chan['id'], 'name' : chan['name']})
    return {
        'channels' : channels
    }

def channels_listall_v1(auth_user_id):
    """ Lists all channels that exist including public and private channels.

        Arguments:
            auth_user_id (int)    - The user id of the calling user.

        Exceptions:
            AccessError - Occurs when the user's id does not exist in the data store.

        Return Value:
            Returns { channels } on successful completion.
    """

    # Verifies that the user exists in the data store, raises an AccessError otherwise.
    if not verify_user_id(auth_user_id):
        raise AccessError

    # Iterates through the list of channels and adds them to channels list.
    store = data_store.get()
    channel_store = store['channels']
    channels = []

    for chan in channel_store:
        channels.append({'channel_id' : chan['id'], 'name' : chan['name']})

    # Return the channels list as a value of key channels in a dictionary.
    return {
        'channels' : channels
    }

def channels_create_v1(auth_user_id, name, is_public):
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

    # Verifies that the user exists in the data store, raises an AccessError otherwise.
    if not verify_user_id(auth_user_id):
        raise AccessError

    # Verifies that the channel name is of correct length, raises an InputError otherwise.
    if len(name) < 1 or len(name) > 20:
        raise InputError

    # Creates the channel if call is valid
    # Channel dictionary entry is as follows:
    #     'id'            :   integer type - assigned sequentially
    #     'name'          :   string type
    #     'is_public'     :   boolean
    #     'owner_members' :   list of user ids - creator made an owner
    #     'all_members'   :   list of user ids - creator made a member
    #     'messages'      :   list of dictionaries for message details i.e.
    #                         { message_id, u_id, message, time_created }
    store = data_store.get()
    channels = store['channels']
    new_channel = {
        'id': len(channels) + 1,
        'name' : name,
        'is_public' : is_public,
        'owner_members' : [auth_user_id],
        'all_members' : [auth_user_id],
        'messages' :[],
        }
    channels.append(new_channel)
    data_store.set(store)
    return {
        'channel_id' : new_channel['id']
    }
