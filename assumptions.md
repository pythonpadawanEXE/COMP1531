# Assumptions
This is the list of assumptions made by T11B_DODO whilst developing iteration 1 of Streams for the COMP1531 Major Project.
## channels.py
### `channels_create_v1`
* **Assumption 1:** When an InputError is raised the function will return `None` instead of a `{ channel_id }`.