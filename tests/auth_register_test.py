from src import auth
import re
import pytest
'''
Valid Email Tests
'''
#r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"

def test_valid_email_1():
    result = auth.auth_register_v1('validemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result,int)

'''
Invalid Email Tests
'''
#r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$"

def test_invalid_email_1():
    with pytest.raises(InputError):
        result = auth.auth_register_v1('invalidemailgmail.com', '123abc!@#', 'Hayden', 'Everest')


'''
Invalid Email address is already being used by another user
'''
def test_duplicate_email():

    result = auth.auth_register_v1('duplicateemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    with pytest.raises(InputError):
        auth.auth_register_v1('duplicateemail@gmail.com', '123abc!@#', 'Hayden', 'Everest') # Expect fail since we already registered

'''
Valid Multiple Registrations with unique emails
'''
def test_multiple_emails():
    result = auth.auth_register_v1('distinctemail1@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result,int)
    result = auth.auth_register_v1('distinctemail2@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result,int)
    result = auth.auth_register_v1('distinctemail3@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    assert isinstance(result,int)
'''
Invalid length of password is less than 6 characters
'''
def test_invalid_short_password():
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail@gmail.com', 'short', 'Hayden', 'Everest')

'''
Valid length of password is more than 6 characters
'''
def test_invalid_short_password():
    result = auth.auth_register_v1('validemail@gmail.com', 'nottooshort', 'Hayden', 'Everest')
    assert isinstance(result,int)

'''
Invalid length of name_first is not between 1 and 50 characters inclusive
'''

def test_name_first_invalid_length_short():
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail@gmail.com', '123ab78', '', 'Lastname')

def test_name_first_invalid_length_long():
    str_name = 'TpRXVggwnkBUGjXLVmwEGatLCEpUtbfVFLhDQUqLztGqxnrhruFyPmG'
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail@gmail.com', '123ab78', str_name, 'Lastname')
'''
Valid length of name_first is  between 1 and 50 characters inclusive
'''
def test_name_first_valid_length_1():
    str_name = 'John'
    result = auth.auth_register_v1('validemail@gmail.com', '123ab78', str_name, 'Lastname')
    assert isinstance(result,int)

def test_name_first_valid_length_2():
    str_name = 'John-Mayer'
    result = auth.auth_register_v1('validemail@gmail.com', '123ab78', str_name, 'Lastname')
    assert isinstance(result,int)
'''
Invalid length of name_last is not between 1 and 50 characters inclusive
'''
def test_name_last_invalid_length_short():
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail@gmail.com', '123ab78', 'Firstname', '')

def test_name_last_invalid_length_long():
    str_name = 'TpRXVggwnkBUGjXLVmwEGatLCEpUtbfVFLhDQUqLztGqxnrhruFyPmG'
    with pytest.raises(InputError):
        result = auth.auth_register_v1('validemail@gmail.com', '123ab78', 'Firstname', str_name)

'''
Valid length of name_last is  between 1 and 50 characters inclusive
'''
def test_name_last_valid_length_1():
    str_name = 'John'
    result = auth.auth_register_v1('validemail@gmail.com', '123ab78', 'Firstname', str_name)
    assert isinstance(result,int)

def test_name_last_valid_length_2():
    str_name = 'John-Mayer'
    result = auth.auth_register_v1('validemail@gmail.com', '123ab78', 'Firstname', str_name)
    assert isinstance(result,int)



#     PASSWORD FUTURE WARNINGS
# =================================
#???