#!/bin/bash

# This script will only work when called by a user that also exists
# at the target host and is capable of `sudo`.

# "-K" is necessary because ansible has to prompt
# for a password when becoming a required user.
.venv/bin/ansible-playbook -K $@
