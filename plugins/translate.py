#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""
translate.py

Translate Format
"""
from .vendor.papago import Papago, check_language

def translate_text(author, channel_name, message):
    """ (str, str, str) -> str

    Translate text and output
    """
    current_lang = check_language(message)
    result = {}

    if current_lang == "Japanese":
        result[':flag_jp:'] = message
        result[':flag_kr:'] = Papago.translate_text("ja", "ko", message)
        result[':flag_us:'] = Papago.translate_text("ja", "en", message)
    elif current_lang == "English":
        result[':flag_us:'] = message
        result[':flag_kr:'] = Papago.translate_text("en", "ko", message)
        result[':flag_jp:'] = Papago.translate_text("en", "ja", message)
    elif current_lang == "Korean":
        result[':flag_kr:'] = message
        result[':flag_us:'] = Papago.translate_text("ko", "en", message)
        result[':flag_jp:'] = Papago.translate_text("ko", "ja", message)

    output = f"**@{author[0] + '·' + author[1:]}** from **#{channel_name}** said\n"
    for _key in result:
        result[_key] = result[_key].strip()
        if result[_key] == "":
            return ""
        output += f"> {_key}: {result[_key]}\n"

    return output
