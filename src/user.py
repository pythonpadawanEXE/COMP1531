"""
user.py

This module handles user related functions for the streams web app.

Functions:
    user_profile_v1(auth_user_id, u_id) -> { user }
    user_profile_setname_v1(token, name_first, name_last) -> {}
    user_profile_setemail_v1(token, email) -> {}
    user_profile_sethandle_v1(token, handle_str) -> {}

"""

from src.data_store import data_store
from src.error import InputError, AccessError
from src.other import verify_user_id, check_valid_token, check_email_validity, search_duplicate_email, is_handle_exist

def user_profile_v1(auth_user_id, u_id):
    """ For a valid user, returns information about their user_id, email, first name, last name, and handle
    
        Arguments:
            auth_user_id (int)    - The user ID of the user who is calling user_profile_v1.
            u_id (int)            - The user ID of the user who's profile is being sent.

        Exceptions:
            InputError  - u_id does not refer to a valid user,

            AccessError - the authorised user does not exist

        Return Value:
            Returns { user } on successful completion.
    """
    
    if not verify_user_id(auth_user_id):
        raise AccessError(description="User ID does not exist.")

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

    return {'user' : {
            'u_id': target_user['u_id'],
            'email' : target_user['email'],
            'name_first' : target_user['name_first'],
            'name_last'  : target_user['name_last'],
            'handle_str' : target_user['handle_str']
        }
    }

def user_profile_setname_v1(token, name_first, name_last):
    """ Update the authorised user's first and last name
    
        Arguments:
            token (string)        - The token of the user who is calling user_profile_setname_v1.
            name_first (string)   - The new first name for this user
            name_last (string)    - The new last name for this user

        Exceptions:
            InputError  - length of name_first is not between 1 and 50 characters inclusive
                        - length of name_last is not between 1 and 50 characters inclusive

            AccessError - the authorised user does not exist

        Return Value:
            Returns { } on successful completion.
    """

    # Get the u_id from the token
    u_id = check_valid_token(token)['auth_user_id']

    length_name_first = len(name_first)
    length_name_last = len(name_last)

    # length of name_first is not between 1 and 50 characters inclusive
    if (length_name_first < 1 or length_name_first > 50):
        raise InputError(description="length of name_first is not between 1 and 50 characters inclusive")

    # length of name_last is not between 1 and 50 characters inclusive
    if (length_name_last < 1 or length_name_last > 50):
        raise InputError(description="length of name_last is not between 1 and 50 characters inclusive")

    # Get all users
    store = data_store.get()
    users = store['users']

    # Find the user to be updated
    for user in users:
        if u_id == user['u_id']:
            # Update users name
            user['name_first'] = name_first
            user['name_last'] = name_last

    data_store.save()

    return {}

def user_profile_setemail_v1(token, email):
    """ Update the authorised user's email address
    
        Arguments:
            token (string)        - The token of the user who is calling user_profile_setemail_v1.
            email (string)        - The new email the user wishes to use

        Exceptions:
            InputError  - email entered is not a valid email
                        - email address is already being used by another user

            AccessError - the authorised user does not exist

        Return Value:
            Returns { } on successful completion.
    """

    # Get the u_id from the token
    u_id = check_valid_token(token)['auth_user_id']

    # email entered is not a valid email
    check_email_validity(email)
        
    # email address is already being used by another user
    if search_duplicate_email(email):
        raise InputError(description="email address is already being used by another user")

    # Get all users
    store = data_store.get()
    users = store['users']

    # Find the user to be updated
    for user in users:
        if u_id == user['u_id']:
            # Update the authorised user's email address
            user['email'] = email

    data_store.save()

    return {}

def user_profile_sethandle_v1(token, handle_str):
    """ Update the authorised user's handle (i.e. display name)
    
        Arguments:
            token (string)        - The token of the user who is calling user_profile_sethandle_v1.
            handle_str (string)   - The new email the user wishes to use

        Exceptions:
            InputError  - length of handle_str is not between 3 and 20 characters inclusive
                        - handle_str contains characters that are not alphanumeric
                        - the handle is already used by another user

            AccessError - the authorised user does not exist

        Return Value:
            Returns { } on successful completion.
    """

    # Get the u_id from the token
    u_id = check_valid_token(token)['auth_user_id']

    # length of handle_str is not between 3 and 20 characters inclusive
    length_handle_str = len(handle_str)
    if (length_handle_str < 3 or length_handle_str > 20):
        raise InputError(description="length of handle_str is not between 3 and 20 characters inclusive")

    # handle_str contains characters that are not alphanumeric
    # i.e) a-z, A-Z, 0-9
    if not handle_str.isalnum():
        raise InputError(description="handle_str contains characters that are not alphanumeric")

    # the handle is already used by another user
    if is_handle_exist(handle_str):
        raise InputError(description="the handle is already used by another user")

    # Get all users
    store = data_store.get()
    users = store['users']

    # Find the user to be updated
    for user in users:
        if u_id == user['u_id']:
            # Update the authorised user's handle (i.e. display name)
            user['handle_str'] = handle_str

    data_store.save()

    return {}
