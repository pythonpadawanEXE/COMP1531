# channels-list-v1_test.py
# pytest file to test the implementation of channels_list_v1

import pytest

from src.channels import channels_create_v1, channels_list_v1

def test_valid_list():
    list_of_channels = []
    list_of_channels.append(channels_create_v1(1, "Chan 1", True))
    list_of_channels.append(channels_create_v1(1, "Chan 2", True))
    list_of_channels.append(channels_create_v1(1, "Chan 3", True))
    bad_chan = channels_create_v1(2, "Chan 4", True)
    channels = channels_list_v1(1)
    for channel in list_of_channels:
        assert(channel in channels)
    assert(bad_chan not in channels)

