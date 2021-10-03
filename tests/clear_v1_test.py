from src import other
import pytest
from src.data_store import data_store

def test_clear_v1_check_store():
    other.clear_v1()
    store = data_store.get()
    messages = []
        # replace assertions by conditions
    if not store['users']:
        messages.append("Users is  empty")
    if not store['channels']:
        messages.append("Channels is  empty")

    if not store['passwords']:
        messages.append("Passwords is  empty")

    # assert no error message has been registered, else print messages
    assert len(messages) == 3, "actions occured:\n{}".format("\n".join(messages))


def test_clear_v1():
    assert other.clear_v1() == {}


