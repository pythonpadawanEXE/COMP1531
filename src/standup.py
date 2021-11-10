"""
standup.py

This module handles standup related functionality for the streams web app.

Functions:
    standup_start_v1(auth_user_id, channel_id, length) -> { time_finish }
    standup_send_v1(auth_user_id, channel_id, message)
    standup_active_v1(auth_user_id, channel_id)

"""
import datetime
import threading
from src.data_store import data_store
from src.error import AccessError, InputError
from src.other import get_all_user_id_channel, is_channel_valid

def standup_start_v1(auth_user_id, channel_id, length):
    
    # Check valid call
    if not is_channel_valid(channel_id):
        raise InputError(description="channel_id does not refer to a valid channel")
    
    if auth_user_id not in get_all_user_id_channel(channel_id):
        raise AccessError(description="channel_id is valid and the authorised user is not a member of the channel")
    
    if length < 0:
        raise InputError(description="length is a negative number")
    
    if standup_active_v1(auth_user_id, channel_id)['is_active']:
        raise InputError(description="an active standup is currently running in the channel")
    
    # Calculate finish time    
    time_finish = int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp()) + length
    
    # Get channel
    store = data_store.get()
    channels = store['channels']
    target_channel = {}
    for channel in channels:
        if channel['id'] == channel_id:
            target_channel = channel
            
    # Standup dict entry is as follows:
    #    'author' : u_id of calling user who will send the standup once concluded
    #    'time_finish' : utc_timestamp calculated as current time + length
    #    'standup_message : string type initially empty, standup_send_v1 to concatenate to this str
    target_channel['standup'] = {
        'author' : auth_user_id,
        'time_finish' : time_finish,
        'standup_message' : ""
    }
    
    data_store.set(store)
    
    # Start timer in seperate thread to end standup
    t = threading.Timer(length, standup_end, [channel_id])
    t.start()
    
    return {'time_finish' : time_finish}


def standup_send_v1(auth_user_id, channel_id, message):
    pass

def standup_active_v1(auth_user_id, channel_id):
    
    # Check valid call
    if not is_channel_valid(channel_id):
        raise InputError(description="channel_id does not refer to a valid channel")
    
    if auth_user_id not in get_all_user_id_channel(channel_id):
        raise AccessError(description="channel_id is valid and the authorised user is not a member of the channel")
    
    # Set initial return values
    is_active = False
    time_finish = None
    
    # Get standup dict in channel
    store = data_store.get()
    channels = store['channels']
    target_channel = {}
    for channel in channels:
        if channel['id'] == channel_id:
            target_channel = channel
    standup = target_channel['standup']
    
    # Update return values
    if standup != {}:
        is_active = True
        time_finish = standup['time_finish']
    
    return {
        'is_active' : is_active,
        'time_finish' : time_finish
    }

def standup_end(channel_id):
    
    # Get active standup
    store = data_store.get()
    channels = store['channels']
    target_channel = {}
    for channel in channels:
        if channel['id'] == channel_id:
            target_channel = channel
    print("TARGET CHANNEL")
    print(target_channel)
    standup = target_channel['standup']

    # Send standup message as author
    message = standup['standup_message']
    standup_message(standup['author'], channel_id, message)
    
    # Reset standup dict in channel
    target_channel['standup'] = {}
    data_store.set(store)
    print(f"FINISHED {int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp())}")
    
def standup_message(auth_user_id, channel_id, message_input):
    store = data_store.get()
    channels = store['channels']
    store_messages = store['messages']
    messages = None
    channel_exists = False

    #check if channel exists and auth_user_id in channel members
    for channel in channels:
        if channel['id'] == channel_id:
            channel_exists = True
            if auth_user_id not in channel["all_members"]:
                raise AccessError("User is not an owner or member of this channel.")
            
            
    #raise error if channel does not exist
    if channel_exists == False:
        raise InputError("Channel ID is not valid or does not exist.")

    messages = channel['messages']
    

    message_id = len(store_messages)
    #create new message
    new_message ={
            'dm_id': None,
            'channel_id':  channel_id,
            'message_id': message_id,
            'u_id': auth_user_id,
            'message': message_input,
            'time_created': int(datetime.datetime.utcnow()
                            .replace(tzinfo= datetime.timezone.utc).timestamp()),
            }
    #insert message id into channel['messages']      
    messages.insert(0,message_id)
    
    #insert message details into datastore
    store_messages.append(new_message)
    data_store.set(store)