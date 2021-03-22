#!/usr/bin/env python3

"""Collect forecast data from the OpenWeatherMap API."""

import pickle
from datetime import date, datetime
from pathlib import Path
from pprint import pprint
from secrets import openweathermap_api_key as API_KEY
from typing import Any, Callable, Dict, List, Optional, Tuple

import requests
from pydantic import BaseModel

#### ---- Models ---- ####


def get_current_weather(city: str, state: str, country: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{state},{country}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    pprint(response.json())


def get_onecall_data(lat: float, long: float):
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={long}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    pprint(response.json())
    # TODO: tidy data into pydantic model.


def get_openweathermap_data(lat: float, long: float):
    return get_onecall_data(lat=lat, long=long)
