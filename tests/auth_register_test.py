import auth
import re
'''
Valid Email Tests
'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
'''

'''
Invalid Email Tests
'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
'''



'''
email address is already being used by another user
'''
def test_duplicate_email ():

    result = auth.auth_register_v1('duplicateemail@gmail.com', '123abc!@#', 'Hayden', 'Everest')
    with pytest.raises(InputError):
        auth.auth_register_v1('duplicateemail@gmail.com', '123abc!@#', 'Hayden', 'Everest') # Expect fail since we already registered


'''
length of password is less than 6 characters
'''
def test_short_password():



'''
length of name_first is not between 1 and 50 characters inclusive
'''

def test_name_first_invalid_length_short():


def test_name_first_invalid_length_long():

'''
length of name_last is not between 1 and 50 characters inclusive
'''
def test_name_last_invalid_length_short():


def test_name_last_invalid_length_long():

#     PASSWORD FUTURE WARNINGS
# =================================

#Turn these into warnings for auth_register.py
def test_horrible_password(capfd):
    check_password("password") 
    out, err = capfd.readouterr()
    assert out == "Horrible password\n"

def test_poor_password(capfd):
    check_password("abba") 
    out, err = capfd.readouterr()
    assert out == "Poor password\n"

def test_moderate_password(capfd):
    check_password("iamgreatatthis1") 
    out, err = capfd.readouterr()
    assert out == "Moderate password\n"


def test_strong_password(capfd):
    check_password("IreallylikeCOMP1531") 
    out, err = capfd.readouterr()
    assert out == "Strong password\n"

"""
    Test checks if assertion error is raised when password is empty as no spec specifies that the password cannot be empty
    but it is expected that it shouldn't be.
    https://docs.pytest.org/en/stable/capture.html#accessing-captured-output-from-a-test-function
    https://stackoverflow.com/questions/23337471/how-to-properly-assert-that-an-exception-gets-raised-in-pytest 

"""
def test_empty_password(capfd):
    with pytest.raises(Exception) as excinfo:   
        check_password("")
    assert str(excinfo.value) == "password should not be empty" 