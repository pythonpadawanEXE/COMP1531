"""
auth.py 

This module handles login and registration functionality:

Functions:
    auth_login_v1(email, password) -> { auth_user_id }
    auth_register_v1(email, password, name_first, name_last) -> { auth_user_id }
"""
import datetime
import re
from src.data_store import data_store
from src.error import InputError,AccessError
from src.other import check_email_validity, check_password_validity, \
    search_email_password_match, search_duplicate_email, make_handle,return_token,hash,generate_new_session_id,\
    decode_jwt
    #make_token

def auth_login_v1(email, password):
    """ Checks if valid email password combination and returns auth_user_id.

    Arguments:
        email (string)        - The email of the user to be registered.
        password (string)     - The password of the user to be registered.


    Exceptions:
        InputError  - Occurs when email input is invalid or doesn't belong to a user.
                    - Occurs when length of password is invalid or does not match the
                      password email combination.

    Return Value:
        { auth_user_id (int),
         }                          - Upon successful completion.
        
    """
    #check email and password validity
    check_email_validity(email)
    check_password_validity(password)

    #get authorised user dict for email password combination which acts as a unique key
    auth_dict = search_email_password_match(email,password)
    return {
        'auth_user_id' : auth_dict['auth_user_id']
    }

def auth_register_v1(email, password, name_first, name_last):
    """ Create a unique user dictionary in the users data store with
        the provided inputs and creates a unique handle and id and creates a password
        in the passwords dictionary. Makes a session.

    Arguments:
        email (string)        - The email of the user to be registered.
        password (string)     - The password of the user to be registered.
        name_first (string)   - The first name of the user to be registered.
        name_last (string)    - The last name of the user to be registered.

    Exceptions:
        InputError  - Occurs when email input is invalid or duplicated,
                    - Occurs when  length of password is less than 6 characters  or invalid.
                    - Occurs when length of name_first or name_last is less than 1 character
                    or greater than or equal to 50 characters

    Return Values:
        { auth_user_id (int),
          token        (string),
         }                          - Upon successful completion.
        
    """
    max_name_len = 50
    min_name_len = 1

    #check if email input is duplicate
    if search_duplicate_email(email) != 0:
        raise InputError("Duplicate Email")

    check_email_validity(email)
    check_password_validity(password)

    #check if name_first and name_last fits length constraints
    if len(name_first) > max_name_len or len(name_first) < min_name_len:
        raise InputError("Invalid First Name Length")
    if len(name_last) > max_name_len or len(name_last) < min_name_len:
        raise InputError("Invalid Last Name Length")

    #create new user with 
    store = data_store.get()
    users = store['users']
    passwords = store['passwords']
    u_id = len(users)

    #set permission to normal user
    permission_id = 2
    #if user is first one created give global owner permission
    if len(users) == 0:
        permission_id = 1
    time_stamp = int(datetime.datetime.utcnow().replace(tzinfo= datetime.timezone.utc).timestamp())}
    #add new user to users
    users.append({
            'u_id': u_id,
            'email' : email,
            'name_first' : name_first,
            'name_last'  : name_last,
            'handle_str' : make_handle(name_first,name_last),
            'permission_id': permission_id,
            'sessions' : [],
            'notifications' : [],
            'user_stats': {'channels_joined': [{'num_channels_joined': 0, 'time_stamp': time_stamp}],
                           'dms_joined': [{'num_dms_joined': 0, 'time_stamp': time_stamp}],
                           'messages_sent': [{'num_messages_sent': 0, 'time_stamp': time_stamp}]
            }
        })
    passwords.append({
            'u_id': u_id,
            'password': hash(password),
        })
    store['workspace_stats']['channels_exist'].append({'num_channels_exist': 0, 'time_stamp': time_stamp})
    store['workspace_stats']['dms_exist'].append({'num_dms_exist': 0, 'time_stamp': time_stamp})
    store['workspace_stats'].append([{'num_messages_exist': 0, 'time_stamp': time_stamp}])
    data_store.set(store)
     
    return {
        'auth_user_id': u_id,
    }

def auth_logout_v1(token):
    """ Given a token deocdes the token and removes the session_id assosciated with that token from the database.

    Arguments:
        token (string)        - The encoded token an amlagamation of auth_user_id and session_id


    Return Values:
        { session_id (int)     - Upon successful completion  of old session_id now invalid.
          
         }                         
        
    """
    #get users and decode token
    store = data_store.get()
    users = store['users']
    decoded_token = decode_jwt(token)

    #delete session_id in user's sessions
    for user in users:
        for idx,session in enumerate(user['sessions']):
            if user['u_id'] == decoded_token['auth_user_id'] and decoded_token['session_id'] == session:
                del user['sessions'][idx]     
    data_store.set(store)

    #return old session note not in current use
    return { 'old_session_id' :    decoded_token['session_id']}
   
    
    


