from src.data_store import data_store
from src.error import InputError

def auth_login_v1(email, password):
    return {
        'auth_user_id': 1,
    }

def search_duplicate_email(email):
    store = data_store.get()
    users = store['users']
    count = 0
    for Object in users
        if Object['email'] == email:
            count += 1
    return count

def search_handle(name_first,name_last)
    #TODO: Complete Function
    return new_handle
def auth_register_v1(email, password, name_first, name_last):
    min_password_len = 6
    max_password_len = 128 
    max_name_len = 50
    min_name_len 1
    max_email_user_char = 64
    max_email_domain_char = 64
    max_email_path_char = 256

    if search_duplicate_email(email) != 0:
        raise InputError("Duplicate Email")

    if None == re.fullmatch(r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$',email):
        raise InputError("Invalid Email")
    #https://stackoverflow.com/questions/45082170/regex-to-split-the-email-address-in-python
    email_list = re.findall(r'(.+)@(.+)\.(.+)', email)

    if email_list[0] > max_email_user_char or email_list[1] > max_email_domain_char or email_list[2] > max_email_path_char:
        raise InputError("Email too long")

    if len(password) < min_password_len:
        raise InputError("Password too short!")

    if len(password) > max_password_len:
        raise InputError("Password too long!")
    
    if len(name_first) > max_name_len or len(name_first) < min_name_len:
        raise InputError("Invalid First Name Length")

    if len(name_first) > max_name_len or len(name_first) < min_name_len:
        raise InputError("Invalid First Name Length")



    return {
        'auth_user_id': 1,
    }
