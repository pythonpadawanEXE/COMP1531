'''
dm.py

This module handles creatation, removing, leaving from a dm and listing basic information and details of a dm.

Functions:
    dm_create_v1(auth_user_id, uids) -> {dm_id, name, owner, all_members, messages }
    dm_list_v1(auth_user_id) -> { dms }
    dm_details_v1(auth_user_id, dm_id) -> { name, owner, all member }
    dm_leave_v1(auth_user_id, dm_id) -> {}
    dm_remove_v1(auth_user_id, dm_id) -> {}
    dm_messages_v1(auth_user_id, dm_id, start) -> { messages start end }
    
'''

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import verify_user_id, generate_dm_name, is_dm_valid, get_all_user_id_dm, get_dm_name, is_user_authorised_dm, get_all_members, is_user_creator_dm, get_user_handle, create_notification

def dm_create_v1(auth_user_id, u_ids):
    ''' 
    Creates a dm as specified by the parameters.

    Arguments:
        auth_user_id (int)   - The user id of the calling user.
        u_ids (list)         - The u_id list of the member to be added in.
    
    Return Value:
        Returns { dm_id, name, owner, all members, messages } on successful completion.
    '''

    # Define creator
    creator_u_id = auth_user_id

    # Define list of all members in new dm
    all_members = [creator_u_id]

    # Verifies that the users would be added in dm exist in the data store and add to the all member list of the new dm, raises an InputError
    for u_id in u_ids:
        if not verify_user_id(u_id):
            raise InputError(description = "User not exist.")
        all_members.append(u_id)

    # Creates the dm if call is valid
    # dm dictionary entry is as follows:
    #     'dm_id'        :   integer type - assigned sequentially
    #     'name'         :   string type - alphabetically-sorted, comma-and-space separated list of user handles, e.g. ahandle1, bhandle2, chandle3
    #     'owner'        :   user ids - creator made an owner
    #     'all_members'  :   list of user ids - creator and added members made in all members
    #     'messages'     :   list of dictionaries for message details i.e.
    #                         { message_id, u_id, message, time_created }
    store = data_store.get()
    dms = store['dms']
    new_dm = {
        'dm_id' : len(dms) + 1,
        'name' : generate_dm_name(all_members),
        'owner' : creator_u_id,
        'all_members' : all_members,
        'messages' : [],
    }
    dms.append(new_dm)
    
    for u_id in u_ids:
        create_notification(u_id, -1, new_dm['dm_id'], f"{get_user_handle(creator_u_id)} added you to {new_dm['name']}")
    data_store.set(store)
    return{'dm_id': new_dm['dm_id']}

def dm_list_v1(auth_user_id):
    ''' 
    Lists all dms that exist.

        Arguments:
        auth_user_id (int)    - The user id of the calling user.

        Return Value:
            Returns { dms } on successful completion.
    '''

    # Iterates through the list of dms and adds them to dms list.
    # returns the subset that the given user is a member of.
    store = data_store.get()
    dm_store= store['dms']
    dms = []

    for dm in dm_store:
        if auth_user_id in dm['all_members']:
            dms.append({'dm_id' : dm['dm_id'], 'name' : dm['name']})

    return{
        'dms' : dms
    }

def dm_details_v1(auth_user_id, dm_id):
    ''' 
    Given a dm with ID dm_id that the authorised user is a member of, provide basic
        details about the dm.

        Arguments:
            auth_user_id (int)  - authorised user id of the user who is a member of the dm.
            dm_id (int)         - Dm ID of the dm the user is a member of.

        Exceptions:
            InputError  - Occurs when dm_id does not refer to a valid dm.

            AccessError - Occurs when dm_id is valid and the authorised user is
                          not a member of the dm.

        Return Value:
            Returns { name, owner, all_members } on successful completion.
    '''

    # dm_id does not refer to a valid dm
    if not is_dm_valid(dm_id):
        raise InputError(description = "Dm_id does not refer to a valid dm")
    
    # dm_id is valid and the authorised user is not a member of the dm
    if not is_user_authorised_dm(auth_user_id, dm_id):
        raise AccessError(description = "User not exist in this dm")
    
    # List of auth_user_id of all the members in the dm of ID dm_id
    all_members_id_list = get_all_user_id_dm(dm_id)

    # Return dm details
    return {
        'name': get_dm_name(dm_id),
        'members': get_all_members(all_members_id_list)
    }
    
def dm_leave_v1(auth_user_id, dm_id):
    '''
    Given a dm with ID dm_id that the authorised user is a member of,
    remove them as a member of the dm. Their messages should remain in the dm.
    If the only dm owner leaves, the dm will remain.

        Arguments:
            auth_user_id (int)      - authorised user id of the user who is a member of the dm.
            dm_id (int)             - Dm ID of the dm the user is a member of.

        Exceptions:
            InputError  - Occurs when dm_id does not refer to a valid dm.

            AccessError - Occurs when dm_id is valid and the authorised user is
                          not a member of the dm.

        Return Value:
            Returns { } on successful completion.
    '''
    
    # dm_id does not refer to a valid dm
    if not is_dm_valid(dm_id):
        raise InputError(description = "Dm_id does bot refer to a valid dm.")
    
    # dm_id is valid and the authorised user is not a member of the dm 
    if not is_user_authorised_dm(auth_user_id, dm_id):
        raise AccessError(description = "User not exist in this dm")

    # Get all dms
    store = data_store.get()
    dm_store= store['dms']
    
    # Loop through and find the authorised dm
    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            # Remove auth_user_id from all_members
            dm['all_members'].remove(auth_user_id)

            # If user is owner
            if dm['owner'] == auth_user_id:
                # Remove auth_user_id from owner
                dm['owner'] = None

    # Save the data store           
    data_store.set(store)
    
    return {}

def dm_remove_v1(auth_user_id, dm_id):
    '''
    Given a dm with ID dm_id that the authorised user is a member of,
    removing an existing dm, so all members are no longer in the dm. This can only
    done by the original creator of the dm.

        Arguments:
            auth_user_id (int)      - authorised user id of the user who is a creator of the dm.
            dm_id (int)             - Dm ID of the dm the user is a member of.

        Exceptions:
            InputError  - Occurs when dm_id does not refer to a valid dm.

            AccessError - Occurs when dm_id is valid and the authorised user is
                          not the creator of the dm.

        Return Value:
            Returns { } on successful completion.
    '''

    # dm_id does not refer to a valid dm
    if not is_dm_valid(dm_id):
        raise InputError(description = "Dm_id does bot refer to a valid dm.")

    # dm_id is valid and the authorised user is not the creator of the dm
    if not is_user_creator_dm(auth_user_id, dm_id):
        raise AccessError(description = "User is not the creator of this dm")

    # Get all dms
    store = data_store.get()
    dm_store= store['dms']

    # Loop through and find the authorised dm
    for dm in dm_store:
        if dm['dm_id'] == dm_id:
            # remove the authorised dm from dms in data store
            dm_store.remove(dm)
    data_store.set(store)
    return{}

def dm_messages_v1(auth_user_id, dm_id, start):
    '''
    Given a dm with ID dm_id that the authorised user is a member of and and the 
    starting index of messages to be displayed from. Lists the 50 most recent 
    messages from start.

        Arguments:
            auth_user_id (int)      - User ID of the user who is a member of the dm.
            dm_id (int)             - Dm ID of the dm the user is a member of.
            start (int)             - Starting index of messages to be displayed.

        Exceptions:
            InputError  - Occurs when dm_id does not refer to a valid dm or
                          start is greater than the total number of messages in the dm.
                          or less that 0 which refers to a invalid Start Index.

            AccessError - Occurs when dm_id is valid and the authorised user is not a
                          member of the dm.

        Return Value:
            Returns { messages, start, end } on successful completion.
    '''

    # dm_id does not refer to a valid dm
    if not is_dm_valid(dm_id):
        raise InputError(description = "Dm_id does bot refer to a valid dm.")

    # dm_id is valid and the authorised user is not the member of the dm
    if not is_user_authorised_dm(auth_user_id, dm_id):
        raise AccessError(description = "User not exist in this dm")

    # Start index is invalid if it is less than 0
    if start < 0:
        raise InputError(description = "Invalid Start Index")
    
    # Get all dms
    store = data_store.get()
    dm_store = store['dms']

    # Loop through and find the authorised dm
    for dm in dm_store:
        if dm['dm_id'] == dm_id:

            # Start index is invalid if it is greater than the total number of messages in the dm
            if len(dm['messages']) - 1 < start:
                raise InputError(description = "Invalid Start Index")

    # Get  messages in the authorised dm
    messages_dm = dm['messages']

    # Get all messages
    messages_store = store['messages']

    # Create returned message list
    returned_messages = []

    # 50 is the pagination block of messages
    end = start + 50
    
    # Loop through and find the authorised message in dm 
    for idx , _ in enumerate(messages_dm):
        if start <= idx < end:

            # Add the 50 messages from the start index to the returned message list
            returned_messages.append({
                'message_id': messages_store[messages_dm[idx]]['message_id'],
                'u_id': messages_store[messages_dm[idx]]['u_id'],
                'message': messages_store[messages_dm[idx]]['message'],
                'time_created': messages_store[messages_dm[idx]]['time_created']  
            })

    # If there's nore more messages to load after this return
    if len(dm['messages']) < end:
        end = -1

    return {
        'messages': returned_messages,
        'start': start,
        'end': end,
    }


