#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""
hashcrack.py

Cracking hashes
"""
from .vendor.hashcrack import crack_hash
from collections import Counter

def crack_text(message):
    """ (str) -> str

    Crack text
    """
    output = ""
    result = crack_hash(message)

    if result:
        # Find most common string
        _count = Counter(result)
        output = f":green_heart: Hash cracked! Decrypted as **{_count.most_common(1)[0][0]}**"
    else:
        output = ":warning: Failed to crack hash!"

    return output
