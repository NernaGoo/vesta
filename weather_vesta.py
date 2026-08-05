#!/bin/env python3
# Name: weather_vesta.py
# Get the weather and send to vestaboard note

import os
import requests
from dotenv import load_dotenv
from config import colors, compose_vbml, send_array_to_vestaboard
import json

DEBUG_MODE = False  # Set to True to print out dprint statements
TEST_MODE = False  # Set to True to test dummy values (instead of making API calls & using up free tier credits)

# Load API keys and environment variables
load_dotenv()
weather_api_key = os.getenv("WEATHER_API_KEY")
lat = os.getenv("LAT")  # latitude for weather location
lon = os.getenv("LON")  # longitude for weather location

# Dummy data sources set in local environment
dummy_weather_data = os.getenv("WEATHER_JSON")
dummy_air_data = os.getenv("AIR_JSON")
dummy_forecast_data = os.getenv("FORECAST_JSON")


def dprint(*args, **kwargs):
    if DEBUG_MODE:
        print(*args, **kwargs)


def get_weather(lat, lon, api_key, units="imperial"):
    # https://openweathermap.org/api/current?collection=current_forecast
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    query_params = {
        "units": units,
        "lat": lat,
        "lon": lon,
        "appid": api_key,
    }
    weather_list = {}  # empty list

    if TEST_MODE:
        # ========== TESTING - DUMMY DATA ============ #
        # Open and read the JSON file
        dprint(" !!! DUMMY values !!!")
        with open(dummy_weather_data, "r", encoding="utf-8") as file:
            weather = json.load(file)

    else:
        # Fetch current weather data
        print("Fetching Weather DATA...")
        try:
            weather_response = requests.get(weather_url, params=query_params)
            weather_response.raise_for_status()
            weather = weather_response.json()

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

        else:
            print("  Success!")

    dprint(f"MODULE: weather json: {weather}")  # DEBUG
    rtemp = weather["main"]["temp"]  # raw temperature value
    temp = f"{round(rtemp)}F"  # F symbol
    humidity = f"{weather['main']['humidity']}%"  # % symbol
    conditions = f"{weather['weather'][0]['description']}"
    wind = f"{round(weather['wind']['speed'])}"  # round
    city = f"{weather['name']}"

    # If weather condition string is more than 15 chars, it won't fit single vestaboard line
    # Print only the last word and hope description still makes sense
    conditions = conditions.split()[-1] if len(conditions) > 15 else conditions

    # Extract current weather data from the JSON response and create a list
    weather_list = {
        "rtemp": rtemp,
        "temp": temp,
        "humidity": humidity,
        "conditions": conditions,
        "city": city,
        "wind": wind,
    }

    # =========== DEBUG STATEMENTS ============= #
    dprint(f"MODULE: {weather_list}")

    return weather_list


def get_forecast(lat, lon, api_key, units="imperial"):
    # https://openweathermap.org/api/forecast5?collection=current_forecast
    # take all max temps for current day; get the highest temp in group for the day high
    # take all min temps for current day, get the lowest temp in group for the low
    weather_url = "https://api.openweathermap.org/data/2.5/forecast"
    query_params = {
        "units": units,
        "lat": lat,
        "lon": lon,
        "appid": api_key,
    }

    if TEST_MODE:
        # Load dummy data from json file
        dprint(" !!! DUMMY values !!!")
        with open(dummy_forecast_data, "r", encoding="utf-8") as file:
            forecast = json.load(file)

    else:
        try:
            print("Fetching forecast data...")
            forecast_response = requests.get(weather_url, params=query_params)
            forecast_response.raise_for_status()
            forecast = forecast_response.json()

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

        else:
            print("  Success!")

    dprint(f"MODULE: forecast json: {forecast}")
    max_rtemp = max(item["main"]["temp"] for item in forecast["list"][:8])
    max_temp = f"{round(max_rtemp)}"

    min_rtemp = min(item["main"]["temp"] for item in forecast["list"][:8])
    min_temp = f"{round(min_rtemp)}"

    dprint(f"MODULE: max_temp is {max_temp}")
    dprint(f"MODULE: min_temp is {min_temp}")

    high_and_low_temps = {
        "high_temp": max_temp,
        "low_temp": min_temp,
    }

    return high_and_low_temps


def color_temperature(raw_temp):
    # Assign a color to temperature range to indicate how chilly or hot it is out there
    raw_temp = float(raw_temp)  # convert any strings to float value
    # Temperature color scale
    if raw_temp <= 14:
        color = colors["white"]
    elif raw_temp > 14 and raw_temp <= 32:
        color = colors["violet"]
    elif raw_temp > 32 and raw_temp <= 50:
        color = colors["blue"]
    elif raw_temp > 50 and raw_temp <= 68:
        color = colors["yellow"]
    elif raw_temp > 68 and raw_temp <= 77:
        color = colors["green"]
    elif raw_temp > 77 and raw_temp <= 86:
        color = colors["orange"]
    elif raw_temp > 86:
        color = colors["red"]

    dprint(f"Module: color temp is: {color}")

    return color


def get_air_pollution(lat, lon, api_key, units="imperial"):
    # https://openweathermap.org/api/air-pollution-index-levels?collection=environmental#usa
    pollution_url = "https://api.openweathermap.org/data/2.5/air_pollution"
    query_params = {
        "units": units,
        "lat": lat,
        "lon": lon,
        "appid": api_key,
    }

    # https://openweathermap.org/api/air-pollution?collection=environmental
    aqi_scale = {
        1: "G",  # Good
        2: "F",  # Fair
        3: "M",  # Moderate
        4: "P",  # Poor
        5: "VP",  # Very Poor
    }

    # Fetch air pollution index level
    if not TEST_MODE:
        print("Fetching Air Pollution DATA...")
        try:
            pollution_response = requests.get(pollution_url, params=query_params)
            pollution_response.raise_for_status()
            pollution = pollution_response.json()

        except requests.exceptions.Timeout:
            print("Request timed out.")

        except requests.exceptions.ConnectionError:
            print("Could not connect to the server.")

        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            print(f"Status code: {pollution_response.status_code}")

        except requests.exceptions.JSONDecodeError:
            print("Response was not valid JSON.")

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")

        else:
            print("  Success!")

    else:
        # ========== TESTING - DUMMY DATA ============ #
        dprint(" !!! DUMMY values !!!")
        # Open and read the JSON file
        with open(dummy_air_data, "r", encoding="utf-8") as file:
            pollution = json.load(file)

    dprint(f"MODULE: pollution_json: ${pollution}")  # DEBUG

    # Extract pollution values from data
    aqi = pollution["list"][0]["main"][
        "aqi"
    ]  # <- Air Quality Index: Possible values: 1, 2, 3, 4, 5
    pm2_5 = pollution["list"][0]["components"][
        "pm2_5"
    ]  # <- Сoncentration of PM2.5 (Fine particles matter), μg/m3
    pm10 = pollution["list"][0]["components"][
        "pm10"
    ]  # <- Сoncentration of PM10 (Coarse particulate matter), μg/m3
    co = pollution["list"][0]["components"][
        "co"
    ]  # <- Сoncentration of CO (Carbon monoxide), μg/m3

    # Generate list of current pollution data
    air_list = {
        "aqi": aqi,
        "pm2_5": pm2_5,
        "pm10": pm10,
        "co": co,
    }

    # Translate AQI value: Where 1 = Good, 2 = Fair, 3 = Moderate, 4 = Poor, 5 = Very Poor
    air_quality = aqi_scale.get(air_list["aqi"], "U")

    # =========== DEBUG STATEMENTS ============= #
    dprint(f"MODULE: air: {air_quality}")
    dprint(f"MODULE: air list: {air_list}")

    return air_quality


def main():

    # Get weather conditions for location
    my_weather = get_weather(lat=lat, lon=lon, api_key=weather_api_key)
    dprint(f"my_weather: {my_weather}")  # DEBUG

    air_quality = get_air_pollution(lat=lat, lon=lon, api_key=weather_api_key)
    dprint(f"my air_quality: {air_quality}")

    my_forecast = get_forecast(lat=lat, lon=lon, api_key=weather_api_key)
    dprint(f"my_forecast: {my_forecast}")  # DEBUG

    conditions = my_weather["conditions"]
    temperature = my_weather["temp"]
    humidity = my_weather["humidity"]
    wind = my_weather["wind"]
    color = color_temperature(my_weather["rtemp"])  # DEBUG
    low_temp = my_forecast["low_temp"]
    high_temp = my_forecast["high_temp"]

    weather_props = {
        "temperature": temperature,
        "humidity": humidity,
        "conditions": conditions,
        "wind": wind,
        "aqi": air_quality,
        "color": color,
        "high": high_temp,
        "low": low_temp,
    }

    weather_components = [
        {
            "style": {
                "height": 3,
                "width": 15,
                "justify": "center",
                "align": "center",
            },
            "template": "{{conditions}} {{temperature}}{{color}} L:{{low}} H:{{high}} W:{{wind}} RH:{{humidity}} A:{{aqi}}",
        }
    ]

    # Translate VBML to character array
    characters = compose_vbml(props=weather_props, components=weather_components)

    # =========== DEBUG STATEMENTS ============= #
    dprint(f"characters to send to vestabaord display: {characters}")

    # ============ SEND output to VESTABOARD ============ #
    send_array_to_vestaboard(characters)


if __name__ == "__main__":
    main()
