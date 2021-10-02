from src import other
import pytest
from src.data_store import data_store

def test_clear_v1_check_store():
    other.clear_v1()
    store = data_store.get()
    errors = []
        # replace assertions by conditions
    if store['users']:
        errors.append("Users is not empty")
    if store['channels']:
        errors.append("Channels is not empty")

    if store['passwords']:
        errors.append("Passwords is not empty")

    # assert no error message has been registered, else print messages
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_clear_v1():
    assert other.clear_v1() == {}


