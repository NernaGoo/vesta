#!/usr/bin/python3
# Countdown the number of days to a random event from a list of event dates

import requests
from datetime import datetime, date
import random
import os
from config import compose_vbml, send_array_to_vestaboard, get_a_color
import sys

#  --------------- EVENT LIST -------------- #
# Date format is in YYYY-MM-DD
# For annual events, drop the year
events = {
    "New Year": "01-01",
    "4th of July": "07-04",
    "Petra's Birthday": "08-01",
    "Anniversary": "10-04",
    "Halloween": "10-31",
    "Christmas": "12-25",
    "Thanksgiving": "2026-11-26",
    "Labor Day": "2026-09-07",
    "Vacation": "2026-09-25"
}

def is_valid_date_format(event_date):
    # Check for valid date format
    # First, validate one-time event date format
    try:
        datetime.strptime(event_date, "%Y-%m-%d")
        return True
    except ValueError:
        pass # If it fails, move on to the next test

    # Next, validate annual event date format
    try:
        datetime.strptime(event_date, "%m-%d")
        return True
    except ValueError:
        pass 
        
    # If both failed, the format is invalid
    return False

def main():
    # Get today's date
    today = datetime.now()
    future_events = [] # new list to hold today, annual, or future events; ignore past one-off events

    for event_name, event_date in events.items():
        # is event date in valid format
        if not is_valid_date_format(event_date):
            print(f"Error: {event_name} has invalid date format {event_date}")
            print(f"Date must be in YYYY-m-d or m-d format, like 2040-09-17")
            sys.exit()
            
        # check if event_date is an annual event (no year defined)
        # if so, count down to this year or if event passed, next year
        try:
            target_date = datetime.strptime(event_date, "%Y-%m-%d")
            # if date is today or future day, add to future list
            if target_date.date() >= today.date():
                future_events.append((event_name, target_date))

        except ValueError:
            target_date = datetime.strptime(event_date, "%m-%d")
            target_date = target_date.replace(year=today.year)
            
            if target_date.date() < today.date():
                target_date = target_date.replace(year=today.year + 1)
                
            # Annual events are always in the future (or today), so add them
            future_events.append((event_name, target_date))

    # If no future events, nothing to do
    if not future_events:
        print("No future events found in the list!")
        sys.exit()

    # Pick a random day from event list
    event_name, target_date = random.choice(future_events)

    # Calculate the number of days until future date
    time_difference = target_date.date() - today.date()
    delta_days = time_difference.days  # Number of days until event date

    print(f"Days until {event_name}:\t{delta_days}")

    # Send message to Vestaboard
    props = {
        "event": event_name,
        "days": delta_days,
        "color1": get_a_color(),
        "color2": get_a_color(),
    }

    components = [
        {
            "template": "{{color1}} Days Until {{color1}}\n{{event}}:\n{{color2}} {{days}} {{color2}}"
        }
    ]

    characters = compose_vbml(props=props, components=components)
    send_array_to_vestaboard(characters)


if __name__ == "__main__":
    main()
