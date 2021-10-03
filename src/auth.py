"""
A series of authentication functions including but not limited to:
    -auth_login_v1(email,password)
    -auth_register_V1( email, password, name_first, name_last)
"""
import re
from src.data_store import data_store
from src.error import InputError


def check_email_validity(email):
    """ Checks if email is a valid input and raises an error if it isn't.

    Arguments:
        email(string)     - The email of the user to be registered.

    Exceptions:
        InputError - Occurs when  email does not match a valid email length or pattern.
            
    Return Value:
        None
    """
    max_len_email_user_char = 64
    max_len_email_domain_char = 64
    max_len_email_path_char = 256
    if re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$',email) is None:
        raise InputError("Invalid Email")
    
    #https://stackoverflow.com/questions/45082170/regex-to-split-the-email-address-in-python
    email_list = re.findall(r'(.+)@(.+)\.(.+)', email)

    if (len(email_list[0][0]) > max_len_email_user_char or 
    len(email_list[0][1]) > max_len_email_domain_char or 
    len(email_list[0][2]) > max_len_email_path_char):
        raise InputError("Email too long")

def check_password_validity(password):
    """ Checks if password is a valid input and raises an error if it isn't.

    Arguments:
        password (string)     - The password of the user to be registered.


    Exceptions:
        InputError - Occurs when  password does not match a valid password length.
                    

    Return Value:
        None
    """
    min_password_len = 6
    max_password_len = 128 
    if len(password) < min_password_len:
        raise InputError("Password too short!")

    if len(password) > max_password_len:
        raise InputError("Password too long!")

def search_email_password_match(email,password):
    """ Checks if valid email password combination matches register user and returns auth_user_id.

    Arguments:
        email (string)        - The email of the user to be registered.
        password (string)     - The password of the user to be registered.


    Exceptions:
        InputError - Occurs when  input does not match a valid password email combination.
                    

    Return Value:
        Returns { auth_user_id } on successful completion.
    """
    store = data_store.get()
    users = store['users']
    user_id = None
    for user_dict in users:
        if user_dict['email'] == email:
            user_id = user_dict['u_id']
            break
    if user_id is None:
        raise InputError("No User exists with this email/password combination")

    passwords = store['passwords']
    for password_dict in passwords:
        if password_dict['u_id'] == user_id and password_dict['password'] == password :
            return {
                'auth_user_id': user_id,
            }
    raise InputError("No User exists with this email/password combination")
    

def search_duplicate_email(email):
    """ Searches for duplicate emails and returns a count of the number of matching emails to 
        the provided email input.

    Arguments:
        email (string)        - The email of the user to be registered.


    Exceptions:
            None 

    Return Value:
        Returns { count } on successful completion.
    """
    store = data_store.get()
    users = store['users']
    count = 0
    for user_dict in users:
        if user_dict['email'] == email:
            count += 1
    return count

def search_handle(name_first,name_last):
    """ Searches for existing handles and appends a number as a string to create a unique and 
        valid handle.

    Arguments:
        name_first (string)   - The first name of the user to be registered.
        name_last (string)    - The last name of the user to be registered.

    Exceptions:
            None 

    Return Value:
        Returns { valid_handle } on successful completion.
    """
    store = data_store.get()
    users = store['users']
    len_trunc = 20
    count = 0
    str_handle = ((name_first + name_last)[0:len_trunc]).lower()
    if users:
        for user_object in users:
            #print(user_object)
            if user_object['handle_str'] == str_handle:
                str_handle = str_handle + str(count)
                count += 1

    valid_handle = str_handle        
    return valid_handle

def auth_login_v1(email, password):
    """ Checks if valid email password combination and returns auth_user_id.

    Arguments:
        email (string)        - The email of the user to be registered.
        password (string)     - The password of the user to be registered.


    Exceptions:
        InputError  - Occurs when email input is invalid or doesn't belong to a user.
                    - Occurs when  length of password is invalid or does not match the 
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
    
    #check valid input for name_first i.e. cant be only number or 
    # hyphens cannot contain symbols must contain letters
    if not ( (len(re.findall(r'[A-Za-z]',name_first)) + 
    len(re.findall(r'[\s\-0-9]',name_first)) == len(name_first) 
    and len(re.findall(r'[A-Za-z]',name_first)) > 0)):
        raise InputError("name_first invalid character sequence, sequence "+ 
        "must contain letters can contain numbers,hypens or spaces other characters are forbidden.")

    #check valid input for name_last i.e. cant be only number or 
    # hyphens cannot contain symbols must contain letters
    if not ((len(re.findall(r'[A-Za-z]',name_last)) + 
    len(re.findall(r'[\s\-0-9]',name_last)) == len(name_last) 
    and len(re.findall(r'[A-Za-z]',name_last)) > 0)):
        raise InputError("name_last invalid character sequence, sequence " + 
        "must contain letters can contain numbers,hypens or spaces other characters are forbidden.")

    if len(name_first) > max_name_len or len(name_first) < min_name_len:
        raise InputError("Invalid First Name Length")

    if len(name_last) > max_name_len or len(name_last) < min_name_len:
        raise InputError("Invalid First Name Length")
    
    store = data_store.get()
    users = store['users']
    passwords = store['passwords']
    users.append(
         {
            'u_id': len(users) + 1,
            'email' : email,
            'name_first' : name_first,
            'name_last'  : name_last,
            'handle_str' : search_handle(name_first,name_last),

        }

    )
    passwords.append(
        {
            'u_id': len(users),
            'password': password,
        }
    )
    data_store.set(store)

    return {
        'auth_user_id': len(users),
    }
