# Assumptions

This is the list of assumptions made by **T11B_DODO** whilst developing iteration 1 of Streams for the COMP1531 Major Project.

## auth.py

* Length of Valid Email Address TBC  https://stackoverflow.com/questions/5087426/how-many-sub-domain-are-allowed-for-an-email-id
Email Input follows the standard of RFC821 i.e.
  * The maximum total length of a user name is 64 characters.
  * The maximum total length of a domain name or number is 64 characters.
  * The maximum total length of a reverse-path or forward-path is 256 characters (including the punctuation and element separators).

* Length of Maximum Valid Password TBC 256 as this is allowed max in active directory azure, provides a practical maximum but doesn't allowed a DOS?

* Assume that since str_handle must be alphanumeric (a-z0-9) so  name_first and name_last must be letters or hyphens or spaces or numbers
but name_ vairables cannot be only numbers or only hyphens or only spaces,while they can be only letters.

* Maximum Number of Users with respect to max allowable run time expected 2,000 (perform stress test to estimate?)
* Assume that the `u_id` is assigned sequentially and begins at 1.

## channels.py

### `channels_create_v1`

* Assume that the `channel_id` is assigned sequentially and begins at 1.
* Assume that the creator of a channel is added to both owner members and all members lists.

### `channels_list_v1`

* Assume that "associated details" as described in the specification is only the channel name.

## channel.py

### `channel_messages_v1`

* Assume that start is always greater than or equal to zero.