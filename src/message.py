from src.data_store import data_store
from src.error import InputError,AccessError
from src.other import check_valid_token,is_user_channel_owner,is_user_dm_owner,\
is_global_owner
import datetime

def message_send_dm_v1(auth_user_id, dm_id, message_input):
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
    
    #check if valid length of message
    len_msg = len(message_input)
    if len_msg < 1 or len_msg > 1000:
        raise InputError("Invalid length of message.")

    #get existing dms and messages    
    store = data_store.get()
    dms = store['dms']
    store_messages = store['messages']
    messages = None
    dm_exists = False

    #check if dm exists and auth_user_id in dm members
    for dm in dms:
        if dm['dm_id'] == dm_id:
            dm_exists = True
            if auth_user_id not in dm["all_members"]:
                raise AccessError("User is not an owner or member of this dm.")
            
            
    #raise error if dm does not exist
    if dm_exists == False:
        raise InputError("dm_id is not valid or does not exist.")

    messages = dm['messages']
    
    message_id = len(store_messages)

    #create new message
    new_message ={
            'dm_id': dm_id,
            'channel_id':  None,
            'message_id': message_id,
            'u_id': auth_user_id,
            'message': message_input,
            'time_created': int(datetime.datetime.utcnow()
                            .replace(tzinfo= datetime.timezone.utc).timestamp()),
            }
    #insert message id into dm['messages']    
    messages.insert(0,message_id)
    # messages.append(message_id)
    #insert message details into datastore
    store_messages.append(new_message)

    data_store.set(store)
    return {'message_id': message_id}


def message_send_v1(auth_user_id, channel_id, message_input):
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
    #check valid message length
    len_msg = len(message_input)
    if len_msg < 1 or len_msg > 1000:
        raise InputError("Invalid Length of Message.")
    #get existing channels and messages   
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
    # messages.append(message_id)
    #insert message details into datastore
    store_messages.append(new_message)
    data_store.set(store)
    return {'message_id': message_id}

def message_edit_v1(token,message_id,message):
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
    auth_user_id = check_valid_token(token)['auth_user_id']
    store = data_store.get()

    #check if message_id exists indices available
    if message_id > len(store['messages'])-1:
        raise InputError("Message_id does not refer to a valid message.")

    #check if message has been deleted
    if store['messages'][message_id] is None:
        raise InputError("Message has already been deleted")

    #check valid message length
    if len(message) > 1000:
        raise InputError("Invalid message, length is over 1000 characters.")
    #check token is valid
    

    channel_id = store['messages'][message_id]['channel_id']
    dm_id = store['messages'][message_id]['dm_id']
        
    
    if ((dm_id is None and (is_user_channel_owner(auth_user_id, channel_id) == False and is_global_owner(auth_user_id) == False)) or \
    (channel_id is None and is_user_dm_owner(auth_user_id, dm_id) == False)) and store['messages'][message_id]['u_id'] != auth_user_id:
        raise AccessError("The user is not authorised in this dm/channel.")

    

    

    if message == "":
        _  = message_remove_v1(token,message_id)
    else:    
        store['messages'][message_id]['message'] = message

    data_store.set(store)
    return {}

def message_remove_v1(token,message_id):
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
        None
    '''
    auth_user_id = check_valid_token(token)['auth_user_id']
    store = data_store.get()
    # check message_id does not exist the maximum message_id index
    if message_id > len(store['messages'])-1:
        raise InputError("Message_id does not refer to a valid message.")

    #check message is not deleted
    if store['messages'][message_id] is None:
        raise InputError("Message has already been deleted")

    channel_id = store['messages'][message_id]['channel_id']
    dm_id = store['messages'][message_id]['dm_id']
    
    #code block for deleting channel message
    if channel_id is not None:
        # -1 to adjust for starting id of 1 in index 0
        channel = store['channels'][channel_id-1]
        

        if (dm_id is None and (is_user_channel_owner(auth_user_id, channel_id) == False and is_global_owner(auth_user_id) == False)) and \
        store['messages'][message_id]['u_id'] != auth_user_id:
            raise AccessError("The user is not authorised in this channel.")
       
        for idx,message_id_ch in enumerate(channel['messages']):
            if message_id_ch ==  message_id:
                del channel['messages'][idx]

    #code block for deleting dm message
    if dm_id is not None:    
        # -1 to adjust for starting id of 1 in index 0
        dm = store['dms'][dm_id-1]
        
             
        if (channel_id is None and is_user_dm_owner(auth_user_id, dm_id) == False) and \
        store['messages'][message_id]['u_id'] != auth_user_id:
            raise AccessError("The user is not authorised in this dm.")
        
        for idx,message_id_dm in enumerate(dm['messages']):
            if message_id_dm ==  message_id:
                del dm['messages'][idx]  

    

   

    #make the message_dict None
    store['messages'][message_id] = None
    data_store.set(store)
    return {}
    
