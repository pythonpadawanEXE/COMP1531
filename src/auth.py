"""
auth.py 

This module handles login and registration functionality:

Functions:
    auth_login_v1(email, password) -> { auth_user_id }
    auth_register_v1(email, password, name_first, name_last) -> { auth_user_id }
"""
import re
from src.data_store import data_store
from src.error import InputError,AccessError
from src.other import check_email_validity, check_password_validity, \
    search_email_password_match, search_duplicate_email, make_handle,return_token,hash,generate_new_session_id,\
    decode_jwt, generate_password_reset_code, is_valid_reset_code
    #make_token
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
import smtplib
import os

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

    #add new user to users
    users.append({
            'u_id': u_id,
            'email' : email,
            'name_first' : name_first,
            'name_last'  : name_last,
            'handle_str' : make_handle(name_first,name_last),
            'permission_id': permission_id,
            'sessions' : [],
            'notifications' : []
        })
    passwords.append({
            'u_id': u_id,
            'password': hash(password),
        })
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
   
    
def auth_password_reset_request(email):
    """ 
    Given an email address, if the user is a registered user, 
    sends them an email containing a specific secret code, that when 
    entered in auth/passwordreset/reset, shows that the user trying to reset 
    the password is the one who got sent this email. No error should be raised 
    when passed an invalid email, as that would pose a security/privacy concern. 
    When a user requests a password reset, they should be logged out of all current 
    sessions.

    Arguments:
        email (string)        - The email of the user who is requesting a password reset


    Return Values:
        None                      
        
    """
    #check valid email
    if search_duplicate_email(email) != 1:
        return
    code = generate_password_reset_code(email)    
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()
    smtp.starttls()
    smtp.login('dodostreams2021t3', 'dodo123456!')
    msg = MIMEMultipart()
    msg['Subject'] = "Password Reset"
    msg.attach(MIMEText(f"Use the following 24 digit-code to reset your password: {code}"))
    smtp.sendmail(from_addr="hello@gmail.com",
              to_addrs=[email], msg=msg.as_string())
    smtp.quit()


#how to match reset_code with email or make certain reset code is unique to user?
def auth_password_reset(reset_code,new_password):
    """ 
    Given a reset code for a user, set that user's new password to the password provided.

    Arguments:
        reset_code (string)        - The reset_code of the user who is requesting a password reset
                                        received via email.
        
        new_password (string)      -The password that will replace the old password.


    Return Values:
        None                      
        
    """
    auth_user_id = is_valid_reset_code(reset_code)
    if  auth_user_id == None:
        raise InputError("Invalid Reset Code")
    if len(new_password) < 6:
        raise InputError("Password too short.")

    store = data_store.get()
    reset_code_pairs = store['password_reset_codes']   
    passwords = store['passwords'] 
    for password_dict in passwords:
        for reset_code_pair in reset_code_pairs:
            if reset_code_pair['password_reset_code'] == reset_code and auth_user_id == password_dict['u_id']:
                password_dict['password'] = hash(new_password)
                reset_code_pairs.remove(reset_code_pair)
                data_store.set(store)
                

