"""
admin.py

This module handles admin related functions for the streams web app.

Functions:
    get_global_owners -> [ u_ids ]
    admin_user_remove_v1(auth_user_id, u_id) -> { }
    admin_userpermission_change_v1(auth_user_id, u_id, permission_id)
"""

from src.data_store import data_store
from src.dm import dm_leave_v1, dm_list_v1
from src.error import InputError, AccessError
from src.other import is_global_owner

def get_global_owners():
    """ Returns a list of the u_ids of all global owners """

    store = data_store.get()
    users_store = store['users']
    global_owners = []
    for user in users_store:
        if user['permission_id'] == 1:
            global_owners.append(user)
    return global_owners

def admin_user_remove_v1(auth_user_id, u_id):
    """ Given a user by their u_id, remove them from the Streams. 
    
        Arguments:
            auth_user_id (int)    - The user ID of the user who is calling remove.
            u_id (int)            - The user ID of the user who is being removed.

        Exceptions:
            InputError  - u_id does not refer to a valid user,
                        - u_id refers to a user who is the only global owner,

            AccessError - the authorised user is not a global owner,

        Return Value:
            Returns { } on successful completion.
    """

    if not is_global_owner(auth_user_id):
        raise AccessError(description="The authorised user is not a global owner")

    global_owners = get_global_owners()
    if len(global_owners) == 1 and global_owners[0]['u_id'] == u_id:
        raise InputError(description="u_id refers to a user who is the only global owner")
    
    found = False
    target_user = {}
    store = data_store.get()
    users_store = store['users']
    for user in users_store:
        if u_id == user['u_id']:
            found = True
            target_user = user

    if not found:
        raise InputError(description="u_id does not refer to a valid user")

    # Purge user details
    target_user['name_first'] = 'Removed'
    target_user['name_last'] = 'user'
    target_user['email'] = ""
    target_user['handle_str'] = "Removed user"
    
    # Purge user from channel membership
    channels_store = store['channels']
    for channel in channels_store:
        if u_id in channel['owner_members']:
            channel['owner_members'].remove(u_id)

        if u_id in channel['all_members']:
            channel['all_members'].remove(u_id)

    # Purge user from dms
    dms = dm_list_v1(u_id)['dms']
    for dm in dms:
        dm_leave_v1(u_id, dm['dm_id'])

    # Purge user's message contents
    messages_store = store['messages']
    for message in messages_store:
        if message['u_id'] == u_id:
            message['message'] = "Removed user"
    
    data_store.set(store)

    return {}

def admin_userpermission_change_v1(auth_user_id, u_id, permission_id):
    """ Given a user by their user ID, set their permissions to new permissions described by permission_id.
    
        Arguments:
            auth_user_id (int)    - The user ID of the user who is changing the permissions.
            u_id (int)            - The user ID of the user who's permissions are being changed.
            permission_id         - The permission id (1 or 2) the user will have.

        Exceptions:
            InputError  - u_id does not refer to a valid user.
                        - u_id refers to a user who is the only global owner and they are being demoted to a user.
                        - permission_id is invalid.

            AccessError - the authorised user is not a global owner

        Return Value:
            Returns { } on successful completion.
    """
    
    if not is_global_owner(auth_user_id):
        raise AccessError(description="The authorised user is not a global owner")

    if permission_id != 1 and permission_id != 2:
        raise InputError(description="permission_id is invalid")

    global_owners = get_global_owners()
    if len(global_owners) == 1 and global_owners[0]['u_id'] == u_id and permission_id == 2:
        raise InputError(description="u_id refers to a user who is the only global owner")
    
    found = False
    target_user = {}
    store = data_store.get()
    users_store = store['users']
    for user in users_store:
        if u_id == user['u_id']:
            found = True
            target_user = user

    if not found:
        raise InputError(description="u_id does not refer to a valid user")
        
    target_user['permission_id'] = permission_id

    data_store.set(store)

    return {}
