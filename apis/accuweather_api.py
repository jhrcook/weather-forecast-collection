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


class ValueUnit(BaseModel):
    value: float
    unit: str

    class Config:
        alias_generator = to_camel


class MultimetricTemperature(BaseModel):
    metric: ValueUnit
    imperial: ValueUnit

    class Config:
        alias_generator = to_camel


class MinMaxTemperature(BaseModel):
    minimum: ValueUnit
    maximum: ValueUnit

    class Config:
        alias_generator = to_camel


class AccuConditions(BaseModel):
    local_observation_date_time: datetime
    weather_text: str
    has_precipitation: bool
    precipitation: Optional[str]
    is_day_time: bool
    temperature: MultimetricTemperature
    apparent_temperature: MultimetricTemperature
    real_feel_temperature: MultimetricTemperature
    real_feel_temperature_shade: MultimetricTemperature
    relative_humidity: float
    cloud_cover: float

    class Config:
        alias_generator = to_camel


class AccuSummary(BaseModel):
    icon_phrase: str
    has_precipitation: bool
    short_phrase: str
    long_phrase: str
    precipitation_probability: float
    thunderstorm_probability: float
    rain_probability: float
    snow_probability: float
    ice_probability: float
    total_liquid: ValueUnit
    rain: ValueUnit
    snow: ValueUnit
    ice: ValueUnit
    hours_of_precipitation: float
    hours_of_rain: float
    hours_of_snow: float
    hours_of_ice: float
    cloud_cover: float

    class Config:
        alias_generator = to_camel


class AccuDayForecast(BaseModel):
    date: datetime
    temperature: MinMaxTemperature
    real_feel_temperature: MinMaxTemperature
    real_feel_temperature_shade: MinMaxTemperature
    day: AccuSummary
    night: AccuSummary

    class Config:
        alias_generator = to_camel


class AccuHourForecast(BaseModel):
    date_time: datetime
    is_daylight: bool
    temperature: ValueUnit
    real_feel_temperature: ValueUnit
    icon_phrase: str
    has_precipitation: bool
    precipitation_probability: float
    rain_probability: float
    snow_probability: float
    ice_probability: float
    total_liquid: ValueUnit
    rain: ValueUnit
    snow: ValueUnit
    ice: ValueUnit
    cloud_cover: float

    class Config:
        alias_generator = to_camel


class AccuFiveDayForecast(BaseModel):
    effective_date: datetime
    end_date: datetime
    daily_forecasts: List[AccuDayForecast]


class AccuTwelveHourForecast(BaseModel):
    periods: List[AccuHourForecast]


class AccuForecast(BaseModel):
    datetime: datetime
    conditions: AccuConditions
    five_day: AccuFiveDayForecast
    hourly: AccuTwelveHourForecast

    def __str__(self):
        return f"Collected on {self.datetime.strftime('%y-%m-%d %H:%M:%S')}"


#### ---- Getters ---- ####


def cache(func: function) -> Any:
    # TODO: look into a record of locations instead of making another request.
    # TODO: If need to make a request, cache the new key.
    return None


@cache
def get_location_key(lat: float, long: float) -> str:
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


def get_current_conditions(loc_key: str) -> AccuConditions:
    base_url = f"http://dataservice.accuweather.com/currentconditions/v1/{loc_key}?"
    response = requests.get(base_url + f"apikey={API_KEY}&details=true")
    if response.status_code == 200:
        return tidy_current_condition(response.json()[0])
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        raise Exception("Error requesting current conditions from Accuweather.")


def tidy_five_day_forecast(data: Dict[str, Any]) -> AccuFiveDayForecast:
    return AccuFiveDayForecast(
        effective_date=data["Headline"]["EffectiveDate"],
        end_date=data["Headline"]["EndDate"],
        daily_forecasts=[AccuDayForecast(**d) for d in data["DailyForecasts"]],
    )


def get_five_day_forecast(loc_key: str) -> AccuFiveDayForecast:
    base_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{loc_key}?"
    response = requests.get(base_url + f"apikey={API_KEY}&details=true")
    if response.status_code == 200:
        return tidy_five_day_forecast(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        raise Exception("Error requesting forecast data from Accuweather.")


def tidy_hour_forecast(data: List[Dict[str, Any]]) -> AccuTwelveHourForecast:
    return AccuTwelveHourForecast(periods=[AccuHourForecast(**d) for d in data])


def get_twelve_hour_forecast(loc_key: str) -> AccuTwelveHourForecast:
    base_url = (
        f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{loc_key}?"
    )
    response = requests.get(base_url + f"apikey={API_KEY}&details=true")
    if response.status_code == 200:
        # pprint(response.json())
        return tidy_hour_forecast(response.json())
        return None
    else:
        print(f"Error: {response.status_code}")
        pprint(response.json())
        raise Exception("Error requesting hourly forecast data from Accuweather.")


def get_accuweather_forecast(lat: float, long: float) -> AccuForecast:
    location = get_location_key(lat=lat, long=long)
    conditions = get_current_conditions(loc_key=location)
    daily_forecast = get_five_day_forecast(loc_key=location)
    hourly_forecast = get_twelve_hour_forecast(loc_key=location)
    return AccuForecast(
        datetime=datetime.now(),
        conditions=conditions,
        five_day=daily_forecast,
        hourly=hourly_forecast,
    )
