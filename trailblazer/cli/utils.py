# -*- coding: utf-8 -*-
import os


def environ_email():
    """Guess email from sudo user environment variable."""
    username = os.environ.get('SUDO_USER')
    if username:
        return f"{username}@scilifelab.se"
