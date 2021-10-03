"""
auth.py 

This module handles login and registration functionality:

Functions:
    auth_login_v1(email, password) -> { auth_user_id }
    auth_register_v1(email, password, name_first, name_last) -> { auth_user_id }
"""
import re
from src.data_store import data_store
from src.error import InputError
from src.other import check_email_validity, check_password_validity, \
    search_email_password_match, search_duplicate_email, search_handle

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
        Returns { auth_user_id } on successful completion.
    """
    check_email_validity(email)
    check_password_validity(password)
    return search_email_password_match(email,password)

def auth_register_v1(email, password, name_first, name_last):
    """ Create a unique user dictionary in the users data store with
        the provided inputs and creates a unique handle and id and creates a password
        in the passwords dictionary.

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

    Return Value:
        Returns { auth_user_id } on successful completion.
    """
    max_name_len = 50
    min_name_len = 1

    if search_duplicate_email(email) != 0:
        raise InputError("Duplicate Email")

    check_email_validity(email)
    check_password_validity(password)
    # check valid input for name_first i.e. cant be only number or
    # hyphens cannot contain symbols must contain letters
    if not (len(re.findall(r'[A-Za-z]', name_first))+
    len(re.findall(r'[\s\-0-9]',name_first)) == len(name_first) and
    len(re.findall(r'[A-Za-z]',name_first)) > 0):
        raise InputError("name_first invalid character sequence, sequence\
        must contain letters can contain numbers,hypens or spaces other characters are forbidden.")

    # check valid input for name_last i.e. cant be only number or
    # hyphens cannot contain symbols must contain letters
    if not ((len(re.findall(r'[A-Za-z]',name_last))+
    len(re.findall(r'[\s\-0-9]',name_last)) == len(name_last)
    and len(re.findall(r'[A-Za-z]',name_last)) > 0)):
        raise InputError("name_last invalid character sequence, sequence "+
        "must contain letters can contain numbers,hypens or spaces other characters are forbidden.")

    if len(name_first) > max_name_len or len(name_first) < min_name_len:
        raise InputError("Invalid First Name Length")

    if len(name_last) > max_name_len or len(name_last) < min_name_len:
        raise InputError("Invalid First Name Length")
    store = data_store.get()
    users = store['users']
    passwords = store['passwords']
    users.append({
            'u_id': len(users) + 1,
            'email' : email,
            'name_first' : name_first,
            'name_last'  : name_last,
            'handle_str' : search_handle(name_first,name_last),
        })

    passwords.append({
            'u_id': len(users),
            'password': password,
        })
    data_store.set(store)

    return {
        'auth_user_id': len(users),
    }
