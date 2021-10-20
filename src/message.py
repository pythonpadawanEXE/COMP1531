from src.data_store import data_store
from src.error import InputError,AccessError
from src.other import check_valid_token
import datetime

def message_send_v1(auth_user_id, channel_id, message_input):
    '''
    Send a message from the authorised user to the 
    channel specified by channel_id. Note: Each message should have 
    its own unique ID, i.e. no messages should share an ID with another 
    message, even if that other message is in a different channel.
    '''
    len_msg = len(message_input)
    if len_msg < 1 or len_msg > 1000:
        raise InputError("Invalid Length of Message.")
    store = data_store.get()
    channels = store['channels']
    store_messages = store['messages']
    messages = None
    channel_exists = False
    for channel in channels:
        if channel['id'] == channel_id:
            channel_exists = True
            if auth_user_id not in channel["all_members"] and \
                auth_user_id not in channel["owner_members"]:
                raise AccessError("User is not an owner or member of this channel.")
            
            # break

    if not channel_exists:
        raise InputError("Channel ID is not valid or does not exist.")

    messages = channel['messages']
    for message in messages:
        message['message_id'] += 1

    message_id = len(store_messages)
    new_message ={
            'dm_id': None,
            'channel_id':  channel_id,
            'message_id': message_id,
            'u_id': auth_user_id,
            'message': message_input,
            'time_created': int(datetime.datetime.utcnow()
                            .replace(tzinfo= datetime.timezone.utc).timestamp()),
            }
    messages.insert(0,{'message_id':  message_id})
    store_messages.append(new_message)
    data_store.set(store)
    return {'message_id': message_id}