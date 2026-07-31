#!/bin/env python
# Name: msg_vesta.py
# Send a message to Vestaboard Note, or
# Choose a random message from different genres:
# quote, joke, inspiration, trivia, words

import argparse
import os
from dotenv import load_dotenv
import random
from config import send_msg_to_vestaboard, send_array_to_vestaboard, compose_vbml
import re

load_dotenv()


def get_args(parser):
    # print(args)
    # arugments are mutually-exclusive; choose one or the other
    meg = parser.add_mutually_exclusive_group()
    meg.add_argument(
        "-g",
        "--genre",
        choices=["QUOTE", "JOKE", "INSPIRATION", "TRIVIA", "WORDS"],
        default="quote",
        help="Choose a genre. Default is 'quote'",
        type=str.upper,
    )
    meg.add_argument(
        "-m",
        "--message",
        help="Send a message using single-quotes in 45 characters or less.",
    )
    args = parser.parse_args()
    return args


def get_a_msg(file):
    # take data source (file) and pick a random line
    with open(file, "r", encoding="utf-8") as f:
        return random.choice(f.readlines()).strip()


def main():
    # Parse script arguments
    parser = argparse.ArgumentParser()
    args = get_args(parser)

    # print user-provided message otherwise print a random quote based on genre choice
    if args.message:
        msg = args.message
        # Send message to the vestaboard with default formatting
        send_msg_to_vestaboard(msg)
    else:
        genre = args.genre
        print(f"Choice: {genre}")

        # Pick a random note based on genre choice
        file = os.getenv(genre)
        msg = get_a_msg(file)

        # Send message with custom template
        # text, color1, color2 are default props, must be enclosed in double-brackets
        components = [{"template": "{{color2}}{{color1}}{{text}}{{color1}}{{color2}}"}]
        characters = compose_vbml(text=msg, components=components)
        send_array_to_vestaboard(characters)

    print(f"\nMessage: {msg}\n")


if __name__ == "__main__":
    main()
