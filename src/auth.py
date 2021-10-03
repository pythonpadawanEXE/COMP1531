import re
from src.data_store import data_store
from src.error import InputError
from src.other import check_email_validity, check_password_validity, \
    search_email_password_match, search_duplicate_email, search_handle

'''
login user provde either 'auth_user_id': id or raise an input error
'''

def auth_login_v1(email, password):
 
    check_email_validity(email)
    check_password_validity(password)
    
    return search_email_password_match(email,password)

'''
create a unique user dictionary in the users data store with the provided inputs and creates a unique handle and id
'''
def auth_register_v1(email, password, name_first, name_last):
    max_name_len = 50
    min_name_len = 1

    if search_duplicate_email(email) != 0:
        raise InputError("Duplicate Email")

    check_email_validity(email)
    check_password_validity(password)
    
    #check valid input for name_first i.e. cant be only number or hyphens cannot contain symbols must contain letters
    if not (len(re.findall(r'[A-Za-z]',name_first)) + len(re.findall(r'[\s\-0-9]',name_first)) == len(name_first) and len(re.findall(r'[A-Za-z]',name_first)) > 0):
        raise InputError("name_first invalid character sequence, sequence must contain letters can contain numbers,hypens or spaces other characters are forbidden.")

    #check valid input for name_last i.e. cant be only number or hyphens cannot contain symbols must contain letters
    if not (len(re.findall(r'[A-Za-z]',name_last)) + len(re.findall(r'[\s\-0-9]',name_last)) == len(name_last) and len(re.findall(r'[A-Za-z]',name_last)) > 0):
        raise InputError("name_last invalid character sequence, sequence must contain letters can contain numbers,hypens or spaces other characters are forbidden.")

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