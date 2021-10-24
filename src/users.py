"""
users.py

This module allows a user to get a list of all users in the store

Functions:
    users_all_v1() -> { users }
"""

from src.data_store import data_store

def users_all_v1():
    """ Returns a list of all users and their associated details.

        Return Value:
            Returns { users } on successful completion.
    """
    store = data_store.get()
    users_store = store['users']
    users = {'users' : []}
    for user in users_store:
        if user['name_first'] == "Removed":
            continue
        
        users['users'].append({
            'u_id': user['u_id'],
            'email' : user['email'],
            'name_first' : user['name_first'],
            'name_last'  : user['name_last'],
            'handle_str' : user['handle_str']
        })

    return users
