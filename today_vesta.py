#!/usr/bin/env python3
# Send today's date to the Vestaboard

import os
from datetime import date
from config import send_array_to_vestaboard, compose_vbml, get_a_color


def main():
    today = date.today()

    # Date formatted like "Friday March 13, 2026"
    dow = today.strftime(f"%A")
    today_date = today.strftime(f"%B %d, %Y")
    color = get_a_color()
    print(dow)
    print(today_date)

    props = {"day": dow, "date": today_date, "color": color, "line_color": color * 15}

    components = [
        {
            "template": "{{color}}{{day}}{{color}}\n{{date}}\n{{line_color}}",
        }
    ]

    characters = compose_vbml(props=props, components=components)
    send_array_to_vestaboard(characters)


if __name__ == "__main__":
    main()
