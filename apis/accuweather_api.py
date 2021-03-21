#!/usr/bin/env python3

"""Collect forecast data from the Accuweather API."""

from datetime import date, datetime
from pprint import pprint
from secrets import accuweather_api_key as API_KEY
from typing import Any, Dict, List, Optional, Tuple

import requests
import requests_cache
from pydantic import BaseModel, HttpUrl
from requests_cache.backends import base

#### ---- Models ---- ####


def to_camel(string: str) -> str:
    return "".join(word.capitalize() for word in string.split("_"))


class Temperature(BaseModel):
    value: float
    unit: str

    class Config:
        alias_generator = to_camel


class AccuTemperature(BaseModel):
    metric: Temperature
    imperial: Temperature

    class Config:
        alias_generator = to_camel


class AccuConditions(BaseModel):
    local_observation_date_time: datetime
    weather_text: str
    has_precipitation: bool
    precipitation: Optional[str]
    is_day_time: bool
    temperature: AccuTemperature
    apparent_temperature: AccuTemperature
    real_feel_temperature: AccuTemperature
    real_feel_temperature_shade: AccuTemperature
    relative_humidity: float
    cloud_cover: float

    class Config:
        alias_generator = to_camel


class AccuForecast(BaseModel):
    conditions: AccuConditions


#### ---- Getters ---- ####


def get_location_key(lat: float, long: float) -> str:

    # TODO: look into a record of locations instead of making another request.
    # TODO: If need to make a request, cache the new key.

    base_url = (
        "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?"
    )
    response = requests.get(base_url + f"apikey={API_KEY}&q={lat},{long}&details=true")
    if response.status_code == 200:
        return response.json()["Key"]
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        raise Exception("Error requesting location data from Accuweather.")


def tidy_current_condition(data: Dict[str, Any]) -> AccuConditions:
    return AccuConditions(**data)


def get_current_conditions(lat: float, long: float, loc_key: str) -> AccuConditions:
    base_url = f"http://dataservice.accuweather.com/currentconditions/v1/{loc_key}?"
    response = requests.get(base_url + f"apikey={API_KEY}&details=true")
    if response.status_code == 200:
        return tidy_current_condition(response.json()[0])
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        raise Exception("Error requesting location data from Accuweather.")


def get_accuweather_forecast(lat: float, long: float) -> AccuForecast:
    location = get_location_key(lat=lat, long=long)
    conditions = get_current_conditions(lat=lat, long=long, loc_key=location)

    # TODO: forecasts (https://developer.accuweather.com/accuweather-forecast-api/apis)

    return AccuForecast(conditions=conditions)
