#!/usr/bin/env python3

"""Collect forecast data from The Weather Channel API.

From what I can tell, this API used to be open, but is now only available to
individuals with a "personal weather station" linked with Weather Underground.
"""

from pprint import pprint

import requests

BASE_URL = "https://api.weather.com"


def get_hourly_forecast(lat: float, long: float):
    url = (
        BASE_URL
        + f"/v1/geocode/{lat}/{long}/forecast/hourly/3hour.json?units=m&language=en-US"
    )
    response = requests.get(
        url, headers={"Accept-Encoding": "gzip", "accept": "application/json"}
    )
    pprint(response.json())


def get_weather_channel_data(lat: float, long: float):
    # get_hourly_forecast(lat=lat, long=long)
    raise Exception("This API is not ready for use.")
