# 🚀 Vestaboard Note

Scripts to display messages to Vestaboard Note

## Description

This is a personal project. I wanted ways to automate sending various random messages to a Vestaboard Note from a Raspberry Pi.

## 📌 Table of Contents
- [🚀 Vestaboard Note](#-vestaboard-note)
  - [Description](#description)
  - [📌 Table of Contents](#-table-of-contents)
  - [🔥 Getting Started](#-getting-started)
    - [Prerequisites](#prerequisites)
    - [⚡Installation](#installation)
    - [💡 Usage](#-usage)
      - [Python Scripts](#python-scripts)
      - [Bash Scripts](#bash-scripts)
  - [📝 Reference](#-reference)



## 🔥 Getting Started

### Prerequisites

* python3
* Vestaboard API Key
* OpenWeather API Key
* Finnub.io API Key
* [Vestaboard Note](https://www.vestaboard.com/note)

### ⚡Installation

1. Clone github project
```
git clone https://github.com/NernaGoo/vesta.git
```
2. Set up virtual env
```
sudo apt update
sudo apt install python3-venv
python3 -m venv .venv
source .venv/bin/activate
```
3. Install python modules
```
pip install dotenv argparse requests
``` 

### 💡 Usage

+ Create .env with API keys and file locations
> cat .env
```
FINNHUB_API_KEY="ooooooooooooooooooooooo"
VESTA_API_KEY="ooooooooooooooooooooooo"
LOCAL_VESTA_API_KEY="ooooooooooooooooooooooo"
WEATHER_API_KEY="ooooooooooooooooooooooo"
WORD="ooooooooooooooooooooooo"
QUOTE="ooooooooooooooooooooooo"
JOKE="ooooooooooooooooooooooo"
INSPIRATION="ooooooooooooooooooooooo"
TRIVIA="ooooooooooooooooooooooo"
WEATHER_JSON="ooooooooooooooooooooooo"
AIR_JSON="ooooooooooooooooooooooo"
```

  
+ A cronjob runs hourly from a raspberry pi

```
$ crontab -l
# Runs every hour, starting in the morning
47 9-20 * * * /home/pi/.venv/bin/python /home/pi/vesta/vestaboard_note.py
```


#### Python Scripts
+ config.py
+ countdaysvesta.py
+ history.py
+ msg_vesta.py
+ onthisdayvesta.py
+ quotes_vesta_local.py
+ today_vesta.py
+ vestaboard_note.py
+ weather_vesta.py


#### Bash Scripts
+ defaultvesta.sh
+ eventsvesta.sh
+ morningvesta.sh
+ nexteventvesta.sh
+ stockvesta.sh
+ update_events.sh

## 📝 Reference

* [Vestaboard Cloud API](https://docs.vestaboard.com/docs/read-write-api/introduction/)
* [Finnhub](https://finnhub.io/docs/api/quote)
* [OpenWeather](https://openweathermap.org/api/current?collection=current_forecast)