from src.error import AccessError, InputError
from src.data_store import data_store
import datetime
from src.other import is_channel_valid, is_user_authorised, \
    get_channel_name, is_channel_public, get_channel_owner, \
    user_details, get_all_user_id_channel, get_all_members, \
    verify_user_id


def channel_invite_v1(auth_user_id, channel_id, u_id):
    # Verify the user IDs
    if verify_user_id(auth_user_id) != True:
        raise AccessError

    if verify_user_id(u_id) != True:
        raise InputError
    
    store = data_store.get()

    # Check if call valid
    found_channel_id = False
    target_channel = {}
    channels = store["channels"]
    for channel in channels:
        if channel["id"] == channel_id:
            if auth_user_id not in channel["all_members"] or auth_user_id not in channel["owner_members"]:
                raise AccessError
            
            if u_id in channel["all_members"] or u_id in channel["owner_members"]:
                raise InputError

            found_channel_id = True
            target_channel = channel

    # If channel not found raise InputError
    if found_channel_id != True:
        raise InputError

    # Add user to the target_channel
    target_channel["all_members"].append(u_id)
    data_store.set(store)

    return {
    }

# Given a channel with ID channel_id that the authorised user is a member of,
# provides basic details about the channel.
def channel_details_v1(auth_user_id, channel_id):

    # channel_id does not refer to a valid channel
    if not is_channel_valid(channel_id):
        raise InputError

    # channel_id is valid and the authorised user is not a member of the channel
    if not is_user_authorised(auth_user_id, channel_id):
        raise AccessError

    # auth_user_id of the channel owner of ID channel_id
    channel_owner_id = get_channel_owner(channel_id)

    # List of auth_user_id of all the members in the channel of ID channel_id
    all_members_id_list = get_all_user_id_channel(channel_id)

    # Return channel details
    return {
        'name': get_channel_name(channel_id),
        'is_public': is_channel_public(channel_id),
        'owner_members': user_details(channel_owner_id),
        'all_members': get_all_members(all_members_id_list),
    }

def create_message_v1(auth_user_id,channel_id,message_input):
    store = data_store.get()
    channels = store['channels']
    messages = None
    channel_exists = False
    for channel in channels:
        if channel['id'] == channel_id:
            channel_exists = True
            if auth_user_id not in channel["all_members"] and auth_user_id not in channel["owner_members"]:
                raise AccessError("User is not an owner or member of this channel")
            messages = channel['messages']
            break

    if channel_exists != True:
        raise InputError("Channel ID is not valid or does not exist.")

    
    for message in messages:
        message['message_id'] += 1

    messages.insert(0,
        {
            'message_id': 0,
            'u_id' : auth_user_id,
            'message' : message_input,
            'time_created'  : int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp()),
            #https://stackoverflow.com/questions/55603536/python-time-time-and-datetime-datetime-utcnow-timestamp-returning-differ
        }
        
    )
    data_store.set(store)

def channel_messages_v1(auth_user_id, channel_id, start):
    """
    Returns the 50 most recent messages from start
    """

    store = data_store.get()
    if len(store['users'])+len(store['channels'])+len(store['passwords']) == 0:
        raise InputError("Empty Database")

    channels = store['channels']
    if len(channels) == 0:
        raise InputError("No Channels")
    messages = None
    channel_exists = False
    for channel in channels:
        if channel['id'] == channel_id:
            channel_exists = True
            if auth_user_id not in channel["all_members"] and auth_user_id not in channel["owner_members"]:
                raise AccessError("User is not an owner or member of this channel")
            messages = channel['messages']
            break

    if channel_exists != True:
        raise InputError("Channel ID is not valid or does not exist.")

    if len(messages) < start:
        raise InputError("Start is greater than the total number of messages in the channel")
    end = start + 50
    return_messages = []
    for idx,message in enumerate(messages):
        if start <= idx < end:
            return_messages.append(message)

    if len(return_messages) < end:
        end = -1

    return {
        'messages': return_messages,
        'start': start,
        'end': end,
    }

def channel_join_v1(auth_user_id, channel_id):
    # Verify the user ID
    if verify_user_id(auth_user_id) != True:
        raise AccessError
   
    store = data_store.get()

    # Check if call valid
    found_channel_id = False
    target_channel = {}
    channels = store["channels"]
    for channel in channels:
        if channel["id"] == channel_id:
            # Verify user not in channel
            if auth_user_id in channel["all_members"] or auth_user_id in channel["owner_members"]:
                raise InputError

            # Check if channel public
            elif channel["is_public"] == False:
                raise AccessError

            # Mark channel as found
            else:
                found_channel_id = True
                target_channel = channel

    # If channel not found raise InputError
    if found_channel_id != True:
        raise InputError

    # Add user to the target_channel
    target_channel["all_members"].append(auth_user_id)
    data_store.set(store)
    return {}