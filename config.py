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
from requests.exceptions import (
    HTTPError,
    ConnectionError,
    Timeout,
    RequestException,
)

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
    "!": "{37}",
    "@": "{38}",
    "#": "{39}",
    "$": "{40}",
    "<": "{41}",
    ">": "{42}",
    "-": "{44}",
    "+": "{46}",
    "&": "{47}",
    "=": "{48}",
    ";": "{49}",
    ":": "{50}",
    "'": "{52}",
    '"': "{53}",
    "%": "{54}",
    ",": "{55}",
    ".": "{56}",
    "/": "{59}",
    "?": "{60}",
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

    print("Sending text to vestaboard...")
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Something went wrong. Reason:\n  {e}")


def send_array_to_vestaboard(char_array):
    # https://docs.vestaboard.com/docs/read-write-api/endpoints
    # passthrough for char_array parameter
    url = "https://cloud.vestaboard.com"
    headers = {"X-Vestaboard-Token": api_key}
    payload = {"characters": char_array}

    if char_array is None:
        print("Nothing to send.")

    else:
        try:
            print("Sending message to vestaboard...")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            print("   Success!")

        except Timeout:
            print("Request timed out.")

        except ConnectionError:
            print("Unable to connect to the server.")

        except HTTPError as err:
            print(f"HTTP error: {err}")
            print(f"Status: {response.status_code}")
            print(response.text)

        except ValueError as err:
            print(f"Response error: {err}")

        except RequestException as err:
            print(f"Request failed: {err}")

        except Exception as err:
            print(f"Unexpected error: {err}")


def send_msg_to_vestaboard(text):
    # Sends a message to vestaboard note for display 3x15
    # This reformats text by calling compose_vbml(); uses default props and components
    # https://docs.vestaboard.com/docs/read-write-api/endpoints

    # First, transform text into VBML formatted style, color, and justification
    # Then, send generated character array to board
    print(f"text: {text}")
    char_array = compose_vbml(text)
    send_array_to_vestaboard(char_array)


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

    # Convert text to string
    text = str(text) if text is not None else None

    # Map special characters to character codes to avoid problems with translations
    translation_table = {ord(key): value for key, value in character_codes.items()}
    trtext = text.translate(translation_table) if text is not None else None
    print(f"Text with character codes (props): {trtext}")

    # Set props using the defaults or override with custom values
    # If text=value passed as a parameter, the value overrides the text key/value explicitly set in props
    if props is None:
        final_props = (
            {**DEFAULT_PROPS, "text": trtext} if text is not None else {**DEFAULT_PROPS}
        )
    else:
        # Convert props into strings and replace special characters
        props = {str(k): str(v).translate(translation_table) for k, v in props.items()}
        final_props = {**props, "text": trtext} if text is not None else {**props}
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
        print(f"Something went wrong. Reason:\n  {e}")

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
        response.raise_for_status()
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
