from src import auth
import re
import pytest
from src.data_store import data_store
from src.error import InputError
from src import other

'''
Valid Input
'''

#Valid Email Test
def test_valid_email_1():
    other.clear_v1()
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)

#Valid Multiple Registrations with unique emails

def test_multiple_emails():
    other.clear_v1()
    result1 = auth.auth_register_v1('distinctemail1@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result1['auth_user_id'],int)
    assert isinstance(result1['token'],str)
    result2 = auth.auth_register_v1('distinctemail2@gmail.com', '123abc!@#', 'Bake', 'Everest')
    assert isinstance(result2['auth_user_id'],int)
    assert isinstance(result2['token'],str)
    result3 = auth.auth_register_v1('distinctemail3@gmail.com', '123abc!@#', 'Cake', 'Everest')
    assert isinstance(result3['auth_user_id'],int)
    assert isinstance(result3['token'],str)

    assert result2['auth_user_id'] - result1['auth_user_id'] == 1
    assert result3['auth_user_id'] - result2['auth_user_id'] == 1

#Valid Multiple Registrations with unique lowercase handles
def test_multiple_emails_valid_handles():
    other.clear_v1()
    result1 = auth.auth_register_v1('distinctemail1@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result1['auth_user_id'],int)
    assert isinstance(result1['token'],str)
    result2 = auth.auth_register_v1('distinctemail2@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result2['auth_user_id'],int)
    assert isinstance(result2['token'],str)
    result3 = auth.auth_register_v1('distinctemail3@gmail.com', '123abc!@#', 'Jake', 'Everest')
    assert isinstance(result3['auth_user_id'],int)
    assert isinstance(result3['token'],str)

    store = data_store.get()
    users = store['users']
    print(users)
    assert other.search_handle(result1['auth_user_id']) == "jakeeverest"
    assert other.search_handle(result2['auth_user_id']) == "jakeeverest0"
    assert other.search_handle(result3['auth_user_id']) == "jakeeverest1"
    
    DistinctUsers = list({Object['handle_str']:Object for Object in users}.values())
    
    print(DistinctUsers)
    assert len(users) == len(DistinctUsers)


#Valid length of password is more than 6 characters

def test_valid_len_password():
    other.clear_v1()
    result = auth.auth_register_v1('validemail3@gmail.com', 'nottooshort', 'Hayden', 'Everest')
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)

#Valid length of name_first is  between 1 and 50 characters inclusive

def test_name_first_valid_length_1():
    other.clear_v1()
    str_name = 'John'
    result = auth.auth_register_v1('validemail6@gmail.com', '123ab78', str_name, 'Lastname')
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)

def test_name_first_valid_length_2():
    other.clear_v1()
    str_name = 'John-Mayer'
    result = auth.auth_register_v1('validemail7@gmail.com', '123ab78', str_name, 'Lastname')
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)


#Valid length of name_last is  between 1 and 50 characters inclusive

def test_name_last_valid_length_1():
    other.clear_v1()
    str_name = 'John'
    result = auth.auth_register_v1('validemail10@gmail.com', '123ab78', 'Firstname', str_name)
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)

def test_name_last_valid_length_2():
    other.clear_v1()
    str_name = 'John-Mayer'
    result = auth.auth_register_v1('validemail11@gmail.com', '123ab78', 'Firstname', str_name)
    assert isinstance(result['auth_user_id'],int)
    assert isinstance(result['token'],str)

'''
Input Error
'''
#missing @symbol in email test
def test_invalid_email_1():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('invalidemailgmail.com', '123abc!@#', 'Hayden', 'Everest')

#email too long test 1
def test_invalid_email_too_long_1():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('invalidemailloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong@gmail.com', '123abc!@#', 'Hayden', 'Everest')
#email too long test 2
def test_invalid_email_too_long_2():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('invalidemail@gmailloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong.com', '123abc!@#', 'Hayden', 'Everest')
#email too long test 3
def test_invalid_email_too_long_3():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('invalidemailgmail.comloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong', '123abc!@#', 'Hayden', 'Everest')


#Invalid Email address is already being used by another user

def test_duplicate_email():
    other.clear_v1()
    auth.auth_register_v1('duplicateemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    with pytest.raises(InputError):
        auth.auth_register_v1('duplicateemail@gmail.com', '123abc!@#', 'Hayden', 'Everest') # Expect fail since we already registered

#Invalid length of password is less than 6 characters

def test_invalid_short_password():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('validemail1@gmail.com', 'short', 'Hayden', 'Everest')

#Invalid length of password is more than 256 characters

def test_invalid_long_password():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('validemail2@gmail.com', 'loooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooong', 'Hayden', 'Everest')

#Invalid length of name_first is not between 1 and 50 characters inclusive


def test_name_first_invalid_length_short():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('validemail4@gmail.com', '123ab78', '', 'Lastname')

def test_name_first_invalid_length_long():
    other.clear_v1()
    str_name = 'TpRXVggwnkBUGjXLVmwEGatLCEpUtbfVFLhDQUqLztGqxnrhruFyPmG'
    with pytest.raises(InputError):
        auth.auth_register_v1('validemail5@gmail.com', '123ab78', str_name, 'Lastname')

#Invalid length of name_last is not between 1 and 50 characters inclusive

def test_name_last_invalid_length_short():
    other.clear_v1()
    with pytest.raises(InputError):
        auth.auth_register_v1('validemail8@gmail.com', '123ab78', 'Firstname', '')

def test_name_last_invalid_length_long():
    other.clear_v1()
    str_name = 'TpRXVggwnkBUGjXLVmwEGatLCEpUtbfVFLhDQUqLztGqxnrhruFyPmG'
    with pytest.raises(InputError):
        auth.auth_register_v1('validemail9@gmail.com', '123ab78', 'Firstname', str_name)

'''
Stress Test
'''

#Test Max Users Assumption

def test_valid_max_users_registration():
    other.clear_v1()
    for i in range(2000):
        str_name = 'John' + f'{i}'
        result = auth.auth_register_v1('validemail10'+f'{i}'+ '@gmail.com', '123ab78', 'Firstname', str_name)
        assert isinstance(result['auth_user_id'],int)
        assert isinstance(result['token'],str)

