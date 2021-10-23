from src.data_store import data_store
from src.error import InputError,AccessError
from src.other import check_valid_token,is_user_channel_owner,is_user_dm_owner
import datetime

def message_send_dm_v1(auth_user_id, dm_id, message_input):
    '''
    Send a message from the authorised user to the 
    channel specified by channel_id. Note: Each message should have 
    its own unique ID, i.e. no messages should share an ID with another 
    message, even if that other message is in a different channel.
    '''
    #order errors should be thrown?
    # if Channel_id > len(store['channels']):
    #     raise InputError("Channel ID is not valid or does not exist.")

    len_msg = len(message_input)
    if len_msg < 1 or len_msg > 1000:
        raise InputError("Invalid length of message.")
        
    store = data_store.get()
    dms = store['dms']
    store_messages = store['messages']
    messages = None
    dm_exists = False
    for dm in dms:
        if dm['dm_id'] == dm_id:
            dm_exists = True
            if auth_user_id not in dm["all_members"]:
                raise AccessError("User is not an owner or member of this dm.")
            
            # break

    if dm_exists == False:
        raise InputError("dm_id is not valid or does not exist.")

    messages = dm['messages']
    # for message in messages:
    #     message['message_id'] += 1

    message_id = len(store_messages)
    new_message ={
            'dm_id': dm_id,
            'channel_id':  None,
            'message_id': message_id,
            'u_id': auth_user_id,
            'message': message_input,
            'time_created': int(datetime.datetime.utcnow()
                            .replace(tzinfo= datetime.timezone.utc).timestamp()),
            }
    messages.insert(0,message_id)
    store_messages.append(new_message)
    data_store.set(store)
    return {'message_id': message_id}


def message_send_v1(auth_user_id, channel_id, message_input):
    '''
    Send a message from the authorised user to the 
    channel specified by channel_id. Note: Each message should have 
    its own unique ID, i.e. no messages should share an ID with another 
    message, even if that other message is in a different channel.
    '''
    #order errors should be thrown?
    # if Channel_id > len(store['channels']):
    #     raise InputError("Channel ID is not valid or does not exist.")

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

    if channel_exists == False:
        raise InputError("Channel ID is not valid or does not exist.")

    messages = channel['messages']
    # for message in messages:
    #     message['message_id'] += 1

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
    messages.insert(0,message_id)
    store_messages.append(new_message)
    data_store.set(store)
    return {'message_id': message_id}

def message_edit_v1(token,message_id,message):
    auth_user_id = check_valid_token(token)['auth_user_id']
    store = data_store.get()
    if message_id > len(store['messages'])-1:
        raise InputError("Message_id does not refer to a valid message.")

    #Does this fall under: message_id does not refer to a valid message within a channel/DM that the authorised user has joined?
    #print(f"Check Token store:{store}")
    #print(f"Message dict: {message_dict}, auth_user {auth_user_id}")
    
    if store['messages'][message_id] is None:
        raise InputError("Message has already been deleted")

    if len(message) > 1000:
        raise InputError("Invalid message, length is over 1000 characters.")

    channel_id = store['messages'][message_id]['channel_id']
    dm_id = store['messages'][message_id]['dm_id']

        
    
    if ((dm_id is None and is_user_channel_owner(auth_user_id, channel_id) == False) or \
    (channel_id is None and is_user_dm_owner(auth_user_id, dm_id) == False)) and store['messages'][message_id]['u_id'] != auth_user_id:
        raise AccessError("The user is not authorised in this dm/channel.")

     
    

    if message == "":
        _  = message_remove_v1(token,message_id)
    else:    
        store['messages'][message_id]['message'] = message

    data_store.set(store)
    return {}

def message_remove_v1(token,message_id):
    auth_user_id = check_valid_token(token)['auth_user_id']
    store = data_store.get()
    if message_id > len(store['messages'])-1:
        raise InputError("Message_id does not refer to a valid message.")

    #Does this fall under: message_id does not refer to a valid message within a channel/DM that the authorised user has joined?
    if store['messages'][message_id] is None:
        raise InputError("Message has already been deleted")

    channel_id = store['messages'][message_id]['channel_id']
    dm_id = store['messages'][message_id]['dm_id']
    
    print(f"Check Token store:{store}")
    print(f"Message dict: {store['messages'][message_id]}, auth_user {auth_user_id}")
    if channel_id is not None:
        # -1 to adjust for starting id of 1 in index 0
        channel = store['channels'][channel_id-1]
        

        if (dm_id is None and is_user_channel_owner(auth_user_id, channel_id) == False) and \
        store['messages'][message_id]['u_id'] != auth_user_id:
            raise AccessError("The user is not authorised in this channel.")

        for idx,message_id_ch in enumerate(channel['messages']):
            if message_id_ch ==  message_id:
                del channel['messages'][idx]

    if dm_id is not None:    
        # -1 to adjust for starting id of 1 in index 0
        dm = store['dms'][dm_id-1]
        
             
        if (channel_id is None and is_user_dm_owner(auth_user_id, dm_id) == False) and \
        store['messages'][message_id]['u_id'] != auth_user_id:
            raise AccessError("The user is not authorised in this dm.")
            
        for idx,message_id_dm in enumerate(dm['messages']):
            if message_id_dm ==  message_id:
                del dm['messages'][idx]  

    
    store['messages'][message_id] = None
    data_store.set(store)
    print(f"afer removal {store}")
    return {}
    
