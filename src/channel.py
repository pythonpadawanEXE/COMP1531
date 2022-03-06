"""
channel.py

This module handles joining and invitation of a channel and the details of a channel
such as general information and past message history.

Functions:
    channel_invite_v1(auth_user_id, channel_id, u_id) -> { }
    channel_details_v1(auth_user_id, channel_id) -> { name, is_public, owner_members, all_members }
    channel_messages_v1(auth_user_id, channel_id, start) -> { messages, start, end }
    channel_join_v1(auth_user_id, channel_id) -> { }
"""

from src.error import AccessError, InputError
from src.data_store import data_store
from src.other import is_channel_valid, is_global_owner, is_user_authorised, \
    get_channel_name, is_channel_public, get_channel_owner, \
    user_details, get_all_user_id_channel, get_all_members, \
    verify_user_id, check_valid_token, get_global_owners, create_notification, \
    get_user_handle, update_user_stats_channel_join, update_user_stats_channel_leave
import datetime

def channel_invite_v1(auth_user_id, channel_id, u_id):
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

    # Verify the user IDs
    if not verify_user_id(u_id):
        raise InputError

    store = data_store.get()

    # Check if call valid
    found_channel_id = False
    target_channel = {}
    channels = store["channels"]
    for channel in channels:
        if channel["id"] == channel_id:
            if auth_user_id not in channel["all_members"] or \
            auth_user_id not in channel["owner_members"]:
                raise AccessError

            if u_id in channel["all_members"] or u_id in channel["owner_members"]:
                raise InputError

            found_channel_id = True
            target_channel = channel

    # If channel not found raise InputError
    if not found_channel_id:
        raise InputError

    # Add user to the target_channel
    target_channel["all_members"].append(u_id)
    
    # Notify user    
    create_notification(u_id, target_channel['id'], -1, f"{get_user_handle(auth_user_id)} added you to {target_channel['name']}")
    
    data_store.set(store)

    update_user_stats_channel_join(u_id, int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp()))

    return {}

def channel_details_v1(token, channel_id):
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

    # Get the auth_user_id from the token
    auth_user_id = check_valid_token(token)['auth_user_id']

    # channel_id does not refer to a valid channel
    if not is_channel_valid(channel_id):
        raise InputError(description="channel_id does not refer to a valid channel")

    # channel_id is valid and the authorised user is not a member of the channel
    if not is_user_authorised(auth_user_id, channel_id):
        raise AccessError(description="channel_id is valid and the authorised user is not a member of the channel")

    # list of auth_user_id of the channel owner of ID channel_id
    channel_owner_id_list = get_channel_owner(channel_id)

    # List of auth_user_id of all the members in the channel of ID channel_id
    all_members_id_list = get_all_user_id_channel(channel_id)

    # Return channel details
    return {
        'name': get_channel_name(channel_id),
        'is_public': is_channel_public(channel_id),
        'owner_members': user_details(channel_owner_id_list),
        'all_members': get_all_members(all_members_id_list),
    }

def channel_messages_v1(auth_user_id, channel_id, start):
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
    store = data_store.get()
    
    start = int(start)
    
    channels = store['channels']
    
    messages = None
    channel_exists = False
    
    #check if channel provided exists in datastore and auth_user is a member
    for channel in channels:
        if int(channel['id']) == int(channel_id):
            channel_exists = True
            messages = channel['messages']
            if auth_user_id not in channel["all_members"] and is_global_owner(auth_user_id) == False:
                raise AccessError("User is not an owner or member of this channel")
    
    if start < 0:
        raise InputError("Invalid Start Index")   
    if len(channels) == 0:
        raise InputError("No Channels")
            
    # if channel doesn't exist raise error
    if channel_exists == False:
        raise InputError("Channel ID is not valid or does not exist.")
   
    
    if len(messages) <= start and start != 0:
        raise InputError("Start is greater than the total number of messages in the channel")

    # 50 is the pagination block of messages
    end = start + 50
    return_messages = []
    store_messages = store['messages']
    #note the messages variable is being used to index message_ids
    for idx,_ in enumerate(messages):
        if start <= idx < end:
            return_messages.append({
                'message_id': store_messages[messages[idx]]['message_id'],
                'u_id': store_messages[messages[idx]]['u_id'],
                'message': store_messages[messages[idx]]['message'],
                'time_created': store_messages[messages[idx]]['time_created']

                
            })
    
    #check if more messages to return
    if len(messages) < end:
        end = -1

    #return messages is a dict following messages type in spec
    return {
        'messages': return_messages,
        'start': start,
        'end': end,
    }

def channel_join_v1(auth_user_id, channel_id):
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

    store = data_store.get()

    # Check if call valid
    found_channel_id = False
    target_channel = {}
    channels = store["channels"]
    for channel in channels:
        if channel["id"] == channel_id:
            # Verify user not in channel
            if auth_user_id in channel["all_members"] \
                or auth_user_id in channel["owner_members"]:
                raise InputError(description="The authorised user is already a member of the channel")

            # Check if channel public
            if not channel["is_public"] and not is_global_owner(auth_user_id):
                raise AccessError(description="Channel is private and cannot be joined")

            # Mark channel as found
            found_channel_id = True
            target_channel = channel

    # If channel not found raise InputError
    if not found_channel_id:
        raise InputError(description="Channel does not exist")

    # Add user to the target_channel
    target_channel["all_members"].append(auth_user_id)
    data_store.set(store)
    update_user_stats_channel_join(auth_user_id, int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp()))
    return {}

def channel_leave_v1(token, channel_id):
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

    # channel_id does not refer to a valid channel
    if not is_channel_valid(channel_id):
        raise InputError(description="channel_id does not refer to a valid channel")

    # Get the auth_user_id from the token
    auth_user_id = check_valid_token(token)['auth_user_id']

    # channel_id is valid and the authorised user is not a member of the channel
    if not is_user_authorised(auth_user_id, channel_id):
        raise AccessError(description="channel_id is valid and the authorised user is not a member of the channel")

    # Get all channels
    store = data_store.get()
    channels = store["channels"]

    # Loop through and find the authorised channel
    for channel in channels:
        if (channel_id == channel['id']):
            # Remove auth_user_id from all_members
            channel['all_members'].remove(auth_user_id)

            # If user is owner_member
            if (auth_user_id in channel['owner_members']):
                # Remove auth_user_id from owner_members
                channel['owner_members'].remove(auth_user_id)

    # Save the data store
    data_store.set(store)

    update_user_stats_channel_leave(auth_user_id, int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp()))
    
    return {}

def channel_addowner_v1(token, channel_id, u_id):
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

    # Get the auth_user_id from the token
    auth_user_id = check_valid_token(token)['auth_user_id']

    # List containing channel owners
    channel_owners_list = get_channel_owner(channel_id)

    # List containing global owners
    global_owners_list = get_global_owners()
    
    
    # channel_id is valid and the authorised user does not have owner permissions in the channel
    if (is_channel_valid(channel_id) and auth_user_id not in channel_owners_list and auth_user_id not in global_owners_list):
        raise AccessError(description="channel_id is valid and the authorised user does not have owner permissions in the channel.")

    # channel_id does not refer to a valid channel
    if not is_channel_valid(channel_id):
        raise InputError(description="channel_id does not refer to a valid channel")

    # u_id does not refer to a valid user
    if not verify_user_id(u_id):
        raise InputError(description="u_id does not refer to a valid user")

    # u_id refers to a user who is not a member of the channel
    if not is_user_authorised(u_id, channel_id):
        raise InputError(description="u_id refers to a user who is not a member of the channel")

    # u_id refers to a user who is already an owner of the channel
    if (u_id in channel_owners_list):
        raise InputError(description="u_id refers to a user who is already an owner of the channel")

    # Get all channels
    store = data_store.get()
    channels = store["channels"]

    # Loop through and find the authorised channel
    for channel in channels:
        if (channel_id == channel['id']):
            # Make user with user id u_id an owner of the channel
            channel['owner_members'].append(u_id)

    # Save the data store
    data_store.set(store)

    return {}

def channel_removeowner_v1(token, channel_id, u_id):
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

    # Get the auth_user_id from the token
    auth_user_id = check_valid_token(token)['auth_user_id']

    # List containing channel owners
    channel_owners_list = get_channel_owner(channel_id)

    # List containing global owners
    global_owners_list = get_global_owners()
    
    # channel_id is valid and the authorised user does not have owner permissions in the channel
    if (is_channel_valid(channel_id) and auth_user_id not in channel_owners_list and auth_user_id not in global_owners_list):
        raise AccessError(description="channel_id is valid and the authorised user does not have owner permissions in the channel.")

    # channel_id does not refer to a valid channel
    if not is_channel_valid(channel_id):
        raise InputError(description="channel_id does not refer to a valid channel")

    # u_id does not refer to a valid user
    if not verify_user_id(u_id):
        raise InputError(description="u_id does not refer to a valid user")



    # u_id refers to a user who is not an owner of the channel
    if (u_id not in channel_owners_list):
        raise InputError(description="u_id refers to a user who is not an owner of the channel")

    # u_id refers to a user who is currently the only owner of the channel
    if (u_id in channel_owners_list and len(channel_owners_list) == 1):
        raise InputError(description="u_id refers to a user who is currently the only owner of the channel")

    # Get all channels
    store = data_store.get()
    channels = store["channels"]

    # Loop through and find the authorised channel
    for channel in channels:
        if (channel_id == channel['id']):
            # Remove user with user id u_id as an owner of the channel
            channel['owner_members'].remove(u_id)

    # Save the data store
    data_store.set(store)

    return {}
