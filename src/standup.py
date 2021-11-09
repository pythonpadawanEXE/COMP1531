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
from src.message import message_send_v1
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
    
    # Start timer in seperate thread to end standup
    threading.Timer(length, standup_end, [channel_id])
    data_store.set(store)
    
    return {'time_finish' : time_finish}


def standup_send_v1(auth_user_id, channel_id, message):
    pass

def standup_active_v1(auth_user_id, channel_id):
    pass

def standup_end(channel_id):
    
    # Get active standup
    store = data_store.get()
    channels = store['channels']
    target_channel = {}
    for channel in channels:
        if channel['id'] == channel_id:
            target_channel = channel
    standup = target_channel['standup']
    
    # Send standup message as author
    message = standup['standup_message']
    message_send_v1(standup['author'], channel_id, message) #TODO: Edit to ignore the 1000 char limit as standup message permitted to be longer
    
    # Reset standup dict in channel
    target_channel['standup'] = {}
    data_store.set(store)