from src.data_store import data_store
from src.error import InputError,AccessError
from src.other import check_valid_token, get_all_user_id_channel, is_user_authorised_dm,is_user_channel_owner,is_user_dm_owner,\
is_global_owner, update_user_stats_messages_sent, update_users_stats_messages_exist, is_channel_valid, is_dm_valid, \
get_all_messages_channel, get_all_messages_dm, get_message_string, is_user_authorised, is_user_member_of_channel, get_channel_name, get_dm_name
import datetime
import threading
import re
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
    dm_name = None
    #check if dm exists and auth_user_id in dm members
    for dm in dms:
        if dm['dm_id'] == dm_id:
            dm_exists = True
            dm_name = dm['name']
            messages = dm['messages'] 
            if auth_user_id not in dm["all_members"]:
                raise AccessError("User is not an owner or member of this dm.")
            
            
    #raise error if dm does not exist
    if dm_exists == False:
        raise InputError("dm_id is not valid or does not exist.")

   
    
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
            'reacts' : [],
            'is_pinned': False
            }
    #insert message id into dm['messages']    
    messages.insert(0,message_id)
    
    #insert message details into datastore
    store_messages.append(new_message)
    #if message tags a user(s)
    possible_tags = re.findall(r'(?<=@)[a-zA-Z0-9]*',message_input)
    for tag in possible_tags:
        for user in store['users']:
            if tag == user['handle_str'] and is_user_authorised_dm(user['u_id'],dm_id):
                user['notifications'].append({
                    'channel_id' : -1 ,
                    'dm_id': dm_id,
                    'notification_message':  f"{tag} tagged you in {dm_name}: {message_input[:20]}"  
                })
    data_store.set(store)

    update_user_stats_messages_sent(auth_user_id, new_message['time_created'])
    update_users_stats_messages_exist(int(1), new_message['time_created'])
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
    channel_name = None
    #check if channel exists and auth_user_id in channel members
    for channel in channels:
        if channel['id'] == channel_id:
            channel_name = channel['name']
            messages = channel['messages']
            channel_exists = True
            if auth_user_id not in channel["all_members"]:
                raise AccessError("User is not an owner or member of this channel.")
            
            
    #raise error if channel does not exist
    if channel_exists == False:
        raise InputError("Channel ID is not valid or does not exist.")

    
    

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
            'reacts' : [],
            'is_pinned': False
            }
    #insert message id into channel['messages']      
    messages.insert(0,message_id)
    
    #insert message details into datastore
    store_messages.append(new_message)
    #if message tags a user(s)
    possible_tags = re.findall(r'(?<=@)[a-zA-Z0-9]*',message_input)
    for tag in possible_tags:
        for user in store['users']:
            if tag == user['handle_str'] and is_user_authorised(user['u_id'], channel_id) == True:
                user['notifications'].append({
                    'channel_id' : channel_id ,
                    'dm_id': -1,
                    'notification_message':  f"{tag} tagged you in {channel_name}: {message_input[:20]}"  
                })
    data_store.set(store)
    update_user_stats_messages_sent(auth_user_id, new_message['time_created'])
    update_users_stats_messages_exist(int(1), new_message['time_created'])
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
    if store['messages'][message_id]['message'] is None:
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

    dm_or_channel_name = get_channel_name(channel_id) if dm_id is None else get_dm_name(dm_id)
    
    #if message tags a user(s)
    possible_tags = re.findall(r'(?<=@)[a-zA-Z0-9]*',message)
    for tag in possible_tags:
        for user in store['users']:
            if tag == user['handle_str'] and \
                (is_user_authorised(user['u_id'],channel_id) if dm_id is None else is_user_authorised_dm(user['u_id'],dm_id)):
                user['notifications'].append({
                    'channel_id' : -1 ,
                    'dm_id': dm_id,
                    'notification_message':  f"{tag} tagged you in {dm_or_channel_name}: {message[:20]}"  
                })
    

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
        { }
    '''
    auth_user_id = check_valid_token(token)['auth_user_id']
    store = data_store.get()
    # check message_id does not exist the maximum message_id index
    if message_id > len(store['messages'])-1:
        raise InputError("Message_id does not refer to a valid message.")

    #check message is not deleted
    if store['messages'][message_id]['message'] is None:
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

    #make the message_dict message string None
    store['messages'][message_id]['message'] = None
    data_store.set(store)
    update_users_stats_messages_exist(int(-1), int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp()))
    return {}
    
def message_react(auth_user_id, message_id, react_id):
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
    valid_reacts = [1]
    
    # Find the target message
    store = data_store.get()
    messages = store['messages']
    target_message = {}
    for message in messages:
        if message['message'] is None:
            continue
        if message['message_id'] == message_id:
            target_message = message
    
    if target_message == {}:
        raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined (Does not exist)")
            
    is_dm = target_message['dm_id'] != None
    
    # Check they are in the channel where the message has been sent if not dm
    if not is_dm and auth_user_id not in get_all_user_id_channel(target_message['channel_id']):
        raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined (Channel)")
    
    # Check they are in the dm where the message has been sent if is dm
    if is_dm and not is_user_authorised_dm(auth_user_id, target_message['dm_id']):
        raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined (DM)")
    
    # Check react ID is valid
    if react_id not in valid_reacts:
        raise InputError(description="react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1")
    
    # Check already reacted
    if len(target_message['reacts']) != 0:
        for react_type in target_message['reacts']:
            if react_type['react_id'] == react_id and auth_user_id in react_type['u_ids']:
                raise InputError(description="the message already contains a react with ID react_id from the authorised user")
    
    # React to message
    ## if no reacts
    if len(target_message['reacts']) == 0:
        target_message['reacts'].append({
            'react_id' : react_id, 
            'u_ids' : [auth_user_id]
        })
    ## if react of same type
    else:
        for react_type in target_message['reacts']:
            if react_type['react_id'] == react_id:
                react_type['u_ids'].append(auth_user_id)
                
    data_store.set(store)
    
    return {}

def message_pin(auth_user_id, message_id):
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
    # Find the target message
    store = data_store.get()
    messages = store['messages']
    target_message = {}
    for message in messages:
        if message['message'] is None:
            continue
        if message['message_id'] == message_id:
            target_message = message
    
    if target_message == {}:
        raise InputError(description="message_id is not a valid message within a channel or DM (Does not exist)")

    #Process if message in channel
    if target_message['channel_id'] is not None:
        channel_id = target_message['channel_id'] 
        if is_user_channel_owner(auth_user_id, channel_id) == False and is_global_owner(auth_user_id) == False and\
            is_user_authorised(auth_user_id, channel_id) == True:
           raise AccessError("The authorised user does not have owner permissions in the channel/DM (channel).")
        elif auth_user_id not in get_all_user_id_channel(target_message['channel_id']):
            raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined (Channel)")
        
    #Process if message in dm
    else:   
        dm_id = target_message['dm_id'] 
        if is_user_dm_owner(auth_user_id, dm_id) == False and is_user_authorised_dm(auth_user_id, target_message['dm_id']) == True:
           raise AccessError("The authorised user does not have owner permissions in the channel/DM (dm).")
        # Check they are in the dm where the message has been sent if is dm
        elif not is_user_authorised_dm(auth_user_id, target_message['dm_id']):
            raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined (DM)")
    
    #check if already pinned
    if target_message['is_pinned'] == True:
            raise InputError("The message is already pinned.")
    #set pinned
    else:
        target_message['is_pinned'] = True
    
    data_store.set(store)
    
    return {}

def message_unreact(token, message_id, react_id):
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
    # Verify the token is valid
    auth_user_id = check_valid_token(token)['auth_user_id']

    valid_reacts = [1]

    # Find the target message
    store = data_store.get()
    messages = store['messages']
    target_message = {}
    for message in messages:
        if message['message'] is None:
            continue
        if message['message_id'] == message_id:
            target_message = message

    # message_id is not a valid message within a channel or DM that the authorised user has joined

    if target_message == {}:
        raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined (Does not exist)")
            
    is_dm = target_message['dm_id'] != None
    
    # Check they are in the channel where the message has been sent if not dm
    if not is_dm and auth_user_id not in get_all_user_id_channel(target_message['channel_id']):
        raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined (Channel)")
    
    # Check they are in the dm where the message has been sent if is dm
    if is_dm and not is_user_authorised_dm(auth_user_id, target_message['dm_id']):
        raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined (DM)")
    
    # react_id is not a valid react ID
    if react_id not in valid_reacts:
        raise InputError(description="react_id is not a valid react ID - currently, the only valid react ID the frontend has is 1")
    
    # the message does not contain a react with ID react_id from the authorised user
    no_react_id_from_auth_user = True
    for react_type in target_message['reacts']:
        if react_type['react_id'] == react_id and auth_user_id in react_type['u_ids']:
            react_type['u_ids'].remove(auth_user_id)
            no_react_id_from_auth_user = False
            break

    if no_react_id_from_auth_user:
        raise InputError(description="the message does not contain a react with ID react_id from the authorised user")

    return {}

def message_unpin(auth_user_id, message_id):
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
    # Find the target message
    store = data_store.get()
    messages = store['messages']
    target_message = {}
    for message in messages:
        if message['message'] is None:
            continue
        if message['message_id'] == message_id:
            target_message = message
    
    if target_message == {}:
        raise InputError(description="message_id is not a valid message within a channel or DM (Does not exist)")

    #Process if message in channel
    if target_message['channel_id'] is not None:
        channel_id = target_message['channel_id'] 
        if is_user_channel_owner(auth_user_id, channel_id) == False and is_global_owner(auth_user_id) == False and\
            is_user_authorised(auth_user_id, channel_id) == True:
           raise AccessError("The authorised user does not have owner permissions in the channel/DM (channel).")
        elif auth_user_id not in get_all_user_id_channel(target_message['channel_id']):
            raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined (Channel)")
        
    #Process if message in dm
    else:    
        dm_id = target_message['dm_id'] 
        if is_user_dm_owner(auth_user_id, dm_id) == False and is_user_authorised_dm(auth_user_id, target_message['dm_id']) == True:
           raise AccessError("The authorised user does not have owner permissions in the channel/DM (dm).")
        # Check they are in the dm where the message has been sent if is dm
        elif not is_user_authorised_dm(auth_user_id, target_message['dm_id']):
            raise InputError(description="message_id is not a valid message within a channel or DM that the authorised user has joined (DM)")
    
    #check if already unpinned
    if target_message['is_pinned'] == False:
            raise InputError("The message is already unpinned.")
    #set unpinned
    else:
        target_message['is_pinned'] = False

    data_store.set(store)

    return {}
    
def message_search(token, query_str):
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
    # Check if user is valid
    auth_user_id = check_valid_token(token)['auth_user_id']

    # Check valid query length
    if len(query_str) < 1 or len(query_str) > 1000:
        raise InputError("Invalid query, length is less than 1 or over 1000 characters.")

    # Get data store
    store = data_store.get()
    messages = store['messages']

    matched_messages = []
    for message in messages:
        if message['message'] is None:
            continue
        # Check if authorised user is in the channel or DM of where the message was sent
        if (auth_user_id in get_all_user_id_channel(message['channel_id']) or is_user_authorised_dm(auth_user_id, message['dm_id'])):
            # Check if message contains the query
            if (message['message'].lower()).find(query_str.lower()) != -1:
                # Add message to list of matched messages
                matched_messages.append(
                    {
                    'message_id': message['message_id'],
                    'u_id' : message['u_id'],
                    'message' : message['message'],
                    'time_created' : message['time_created'],
                    'reacts' : message['reacts'],
                    'is_pinned' : message['is_pinned'],
                    }
                )

    return {'messages' : matched_messages}

def message_share(token, og_message_id, channel_id, dm_id, message=''):
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
    # Verify the token is valid
    auth_user_id = check_valid_token(token)['auth_user_id']

    # the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) 
    # and the authorised user has not joined the channel they are trying to share the message to
    if is_channel_valid(channel_id) and dm_id == -1:
        if auth_user_id not in get_all_user_id_channel(channel_id):
            raise AccessError(description="the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user has not joined the channel they are trying to share the message to")

    # the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) 
    # and the authorised user has not joined the DM they are trying to share the message to
    if channel_id == -1 and is_dm_valid(dm_id):
        if not is_user_authorised_dm(auth_user_id, dm_id):
            raise AccessError(description="the pair of channel_id and dm_id are valid (i.e. one is -1, the other is valid) and the authorised user has not joined the DM they are trying to share the message to")

    # both channel_id and dm_id are invalid
    if (not is_channel_valid(channel_id) and not is_dm_valid(dm_id)):
        raise InputError(description="both channel_id and dm_id are invalid")

    # neither channel_id nor dm_id are -1
    if (channel_id != -1 and dm_id != -1):
        raise InputError(description="neither channel_id nor dm_id are -1")

    # og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined
    # find all the messages in a channel/dm where the user is apart of and check if og_message_id is in them
    channel_message_ids = get_all_messages_channel(auth_user_id)
    dm_message_ids = get_all_messages_dm(auth_user_id)

    if (og_message_id not in channel_message_ids and og_message_id not in dm_message_ids):
        raise InputError(description="og_message_id does not refer to a valid message within a channel/DM that the authorised user has joined")

    # length of message is more than 1000 characters
    if len(message) > 1000:
        raise InputError(description="length of message is more than 1000 characters")

    original_msg_str = get_message_string(og_message_id)

    if (channel_id != -1):
        shared_message_id = message_send_v1(auth_user_id, channel_id, f"{original_msg_str} {message}")

    if (dm_id != -1):
        shared_message_id = message_send_dm_v1(auth_user_id, dm_id, f"{original_msg_str} {message}")

    return {'shared_message_id': shared_message_id}

def message_sendlater_v1(token, channel_id, message, time_sent):
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

    # Verify user
    auth_user_id = check_valid_token(token)['auth_user_id']

    # channel_id is valid and the authorised user is not a member of the channel they are trying to post to
    if (is_channel_valid(channel_id) and not is_user_member_of_channel(auth_user_id, channel_id)):
        raise AccessError("channel_id is valid and the authorised user is not a member of the channel they are trying to post to")

    # Check if channel is valid
    if (not is_channel_valid(channel_id)):
        raise InputError("channel_id does not refer to a valid channel")

    # Check valid length of message
    if (len(message) < 1 or len(message) > 1000):
        raise InputError("length of message is less than 1 or over 1000 characters")

    # Check if time_sent is in the past
    if time_sent < int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp()):
        raise InputError("time_sent is in the past")

    send_time = time_sent - int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp())
    # Start timer in seperate thread
    t = threading.Timer(send_time, message_send_v1, [auth_user_id, channel_id, message])
    t.start()

    '''
    You will need to implement it differently. 
    Either by not calling message_send, or by adding an
    optional 'message_id' parameter to message_send so 
    that you can generate the id in advance (though 
    I'm sure many other methods that will work).
    '''

    return {'message_id': message_id}