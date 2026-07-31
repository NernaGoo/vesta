#!/bin/env python
# Name: config.py
# Shared modules and configuration for Vestaboard scripts
# To load config (example):
# from config import colors, compose_vbml, send_array_to_vestaboard

import os
from dotenv import load_dotenv
import random
import requests
from copy import deepcopy

# Load API keys
load_dotenv()
api_key = os.getenv("VESTA_API_KEY")
local_api_key = os.getenv("LOCAL_VESTA_API_KEY")

# https://docs.vestaboard.com/docs/characterCodes
colors = {
    "heart": "{62}",
    "red": "{63}",
    "orange": "{64}",
    "yellow": "{65}",
    "green": "{66}",
    "blue": "{67}",
    "violet": "{68}",
    "white": "{69}",
    "black": "{70}",
}

character_codes = {
    "a": "{1}",
    "b": "{2}",
    "c": "{3}",
    "d": "{4}",
    "e": "{5}",
    "f": "{6}",
    "g": "{7}",
    "h": "{8}",
    "i": "{9}",
    "j": "{10}",
    "k": "{11}",
    "l": "{12}",
    "m": "{13}",
    "n": "{14}",
    "o": "{15}",
    "p": "{16}",
    "q": "{17}",
    "r": "{18}",
    "s": "{19}",
    "t": "{20}",
    "u": "{21}",
    "v": "{22}",
    "w": "{23}",
    "x": "{24}",
    "y": "{25}",
    "z": "{26}",
    "one": "{27}",
    "two": "{28}",
    "three": "{29}",
    "four": "{30}",
    "five": "{31}",
    "six": "{32}",
    "seven": "{33}",
    "eight": "{34}",
    "nine": "{35}",
    "zero": "{36}",
    "exclamation": "{37}",
    "at": "{38}",
    "pound": "{39}",
    "dollar": "{40}",
    "left": "{41}",
    "right": "{42}",
    "hyphen": "{44}",
    "plus": "{46}",
    "ampersand": "{47}",
    "equal": "{48}",
    "semicolon": "{49}",
    "colon": "{50}",
    "single": "{52}",
    "double": "{53}",
    "percent": "{54}",
    "comma": "{55}",
    "period": "{56}",
    "slash": "{59}",
    "question": "{60}",
    "filled": "{71}",
}


def get_a_color():
    # pick a random color from available colors
    return random.choice(list(colors.values()))


def send_text_to_vestaboard(text):
    # https://docs.vestaboard.com/docs/read-write-api/endpoints
    # Simple text
    url = "https://cloud.vestaboard.com"
    headers = {"X-Vestaboard-Token": api_key}
    payload = {"text": text}

    try:
        response = requests.post(url, headers=headers, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def send_array_to_vestaboard(char_array):
    # https://docs.vestaboard.com/docs/read-write-api/endpoints
    # passthrough for char_array parameter
    url = "https://cloud.vestaboard.com"
    headers = {"X-Vestaboard-Token": api_key}
    payload = {"characters": char_array}

    try:
        response = requests.post(url, headers=headers, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


def send_msg_to_vestaboard(text):
    # Sends a message to vestaboard note for display 3x15
    # This reformats text by calling compose_vbml(); uses default props and components
    # https://docs.vestaboard.com/docs/read-write-api/endpoints
    url = "https://cloud.vestaboard.com"
    headers = {"X-Vestaboard-Token": api_key}

    # First, transform text into VBML formatted style, color, and justification
    # Then, send generated character array to board
    print(f"character_array: {text}")
    char_array = compose_vbml(text)
    payload = {"characters": char_array}

    print("Sending message to the Vestaboard Note...")
    try:
        results = requests.post(url=url, headers=headers, json=payload)
        results.raise_for_status()
        print("  Success!")

    except results.exceptions.RequestException as e:
        # This catches ALL requests-related errors
        print(f"An error occurred: {e}")


def deep_merge(default, override):
    # helper function
    # merges custom vbml components with default values
    result = deepcopy(default)

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result


def merge_components(default_components, custom_components=None):
    # helper function
    # merges custom vbml components with default values

    if custom_components is None:
        return deepcopy(default_components)

    merged = deepcopy(default_components)

    for index, custom in enumerate(custom_components):
        if index < len(merged):
            merged[index] = deep_merge(merged[index], custom)
        else:
            # allow user to add new components
            merged.append(custom)

    return merged


def compose_vbml(text=None, props=None, components=None):
    # Generate VBML character array from text string
    # https://docs.vestaboard.com/docs/vbml/
    # takes custom values for props and components if provided otherwise use defaults
    url = "https://vbml.vestaboard.com/compose"
    characters = []

    # Set props using the defaults or override with custom values
    # If text=value passed as a parameter, the value overrides the text key/value explicitly set in props
    if props is None:
        final_props = (
            {**DEFAULT_PROPS, "text": text} if text is not None else {**DEFAULT_PROPS}
        )
    else:
        final_props = {**props, "text": text} if text is not None else {**props}
    # print(f"final_props: {final_props}")

    # Merge components with user-defined values
    final_components = merge_components(DEFAULT_COMPONENTS, components)
    # print(f"final components: {final_components}")

    payload = {
        "style": {"height": 3, "width": 15},  # vestaboard note dimensions
        "props": final_props,
        "components": final_components,
    }

    print("Composing output with VBML characters...")
    try:
        results = requests.post(url, json=payload)
        results.raise_for_status()
        characters = results.json()
        print(f"characters: {characters}")
        print("  Success!")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    return characters


def send_msg_with_local_api(text):
    # Use local api key instead of cloud api
    # https://docs.vestaboard.com/docs/local-api/endpoints
    url = "http://vestaboard.local:7000/local-api/message"
    headers = {"X-Vestaboard-Local-Api-Key": local_api_key}
    char_array = compose_vbml(text)
    payload = {"characters": char_array}

    try:
        print("Sending msg to board using local API")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def send_array_with_local_api(char_array):
    # Use local api key instead of cloud api
    # https://docs.vestaboard.com/docs/local-api/endpoints
    url = "http://vestaboard.local:7000/local-api/message"
    headers = {"X-Vestaboard-Local-Api-Key": local_api_key}
    payload = {"characters": char_array}

    try:
        response = requests.post(url, headers=headers, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


# ----------------- DEFAULT VALUES --------------- #
# Choose random colors and fill up line (15 chars)
color1 = get_a_color()
color2 = get_a_color()
color3 = get_a_color()
line_color = color3 * 15

# Default values for VBML templates
# Wraps a color bit to the text; fills up empty line with color
# See compose_vbml(), values can be overridden by passing parameters to function
# Properties in template should be enclosed with double brackets: {{ }}
# For syntax, see: https://docs.vestaboard.com/docs/vbml
DEFAULT_PROPS = {"line_color": line_color, "color1": color1, "color2": color2}
DEFAULT_COMPONENTS = [
    {
        "style": {"justify": "center", "align": "center"},
        "template": "{{color1}}{{text}}{{color2}}\n{{line_color}}",
    }
]
