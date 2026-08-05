#!/usr/bin/env python
# Name: calendar_vesta.py
# Send calendar events to Vestaboard using google calendar API
# Script takes arguments -o <agenda|next>
# 'agenda' sends today's agenda of events to vestaboard
# 'next' sends the next upcoming single event to the vestaboard
# for calendar, keep event names under 15 chars to fit vestaboard line

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import argparse
from config import (
    compose_vbml,
    send_array_to_vestaboard,
    get_a_color,
    send_text_to_vestaboard,
)
import time

# Load tokens, secrets
load_dotenv()
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
refresh_token = os.getenv("GOOGLE_REFRESH_TOKEN")
calendarId = os.getenv("GOOGLE_CALENDARID")
events_file = os.getenv("EVENTS_FILE")
timezone = os.getenv("TIMEZONE")


def get_args(parser):
    parser.add_argument(
        "-o",
        "--output",
        choices=["agenda", "next"],
        required=True,
        help="agenda: display full day agenda. next: display today's next upcoming apointment",
        type=str.lower,  # case-insensitive
    )

    args = parser.parse_args()
    return args


def get_credentials():
    # ----------  Authentication ---------- #
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=[
            "https://www.googleapis.com/auth/calendar.readonly",
        ],
    )

    # Refresh access token if needed
    creds.refresh(Request())

    return creds


def get_today_calendar(service):
    # ---------- Get today's calendar data ---------- #
    now = datetime.now().astimezone()  # use local timezone

    # Set time range
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)

    events = (
        service.events()
        .list(
            calendarId=calendarId,
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            timeZone=timezone,
            orderBy="startTime",
        )
        .execute()
    )

    return events.get("items", [])


def get_events(calendar):
    # ---------- Return a list of formatted events ---------- #
    events = []
    today = datetime.now().strftime("%A, %B %-d, %Y")

    if calendar:
        for event in calendar:
            summary = event.get("summary", "(No title)")
            start = event["start"]

            # All-day events
            if "date" in start:
                events.append({"DAY": summary})

            # Appointments
            else:
                start_time = datetime.fromisoformat(start["dateTime"])
                events.append({start_time.strftime("%-I:%M%p"): summary})

    return events


def show_agenda(events):
    # ----- Show today's agenda on Vestaboard -------- #
    today = datetime.now().strftime("%A, %B %-d, %Y")
    print(today)
    if not events:
        print("No events or appointments today.")

    else:
        # Vestaboard note can display 3 events at a time
        # So, process events in chunks
        chunk_size = 3

        for event in events:
            for event_time, event_title in event.items():
                print(f"{event_time}\t{event_title}")

        items = list(events)
        for i in range(0, len(items), chunk_size):
            components = []  # start with a blank page
            color = get_a_color()
            chunk = items[i : i + chunk_size]  # take a chunk and process it

            print(f"Page {i // chunk_size + 1}")
            for chunk_event in chunk:
                for event_time, event_title in chunk_event.items():
                    components.append(
                        {
                            "style": {
                                "justify": "left",
                                "align": "top",
                                "height": 1,
                            },
                            "template": f"{event_time}\t{event_title}{color}",
                        },
                    )

            characters = compose_vbml(components=components)
            send_array_to_vestaboard(characters)

            # If last chunk, skip pause
            if i + chunk_size >= len(items):
                print("Done.")
                continue

            print("Pause before displaying next page...\n")
            time.sleep(90)


def get_next_event(events):
    # ---------- Return the next future event ---------- #
    now = datetime.now().time()
    event = []

    for event in events:
        for event_time, event_title in event.items():
            if event_time.startswith("DAY"):
                continue  # skip
            scheduled_time = datetime.strptime(event_time, "%I:%M%p").time()
            if scheduled_time > now:
                return event  # return value when next appointment found

    return event


def show_next_event(events):
    # ---------- Display next event on Vestaboard ---------- #
    event = get_next_event(events)
    if event:
        for event_time, event_title in event.items():
            props = {
                "time": event_time,
                "title": event_title,
                "color1": get_a_color(),
                "color2": get_a_color(),
            }
            components = [
                {
                    "style": {"justify": "center", "align": "center"},
                    "template": "{{color1}}{{color2}} {{time}} {{color2}}{{color1}}\n{{title}}",
                },
            ]

            characters = compose_vbml(props=props, components=components)
            send_array_to_vestaboard(characters)

    else:
        print("No upcoming event today.")


def save_to_file(events):
    with open(events_file, "w") as f:
        for event in events:
            for time, title in event.items():
                f.write(f"{time}\t{title}\n")
    f.close()


def main():
    # parse sript arguments
    parser = argparse.ArgumentParser()
    args = get_args(parser)

    try:
        # Google Calendar API
        creds = get_credentials()
        service = build("calendar", "v3", credentials=creds)

        # Pull calendar events
        calendar = get_today_calendar(service)
        events = get_events(calendar)

        # Save today's events to a local file
        save_to_file(events)

        # Show the next upcoming event on Vestaboard
        if args.output == "next":
            show_next_event(events)

        if args.output == "agenda":
            show_agenda(events)

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
