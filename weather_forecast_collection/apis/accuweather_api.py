#!/usr/bin/env python3

"""Collect forecast data from the Accuweather API."""

import pickle
from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import Any, Callable, Dict, List, Optional

import requests
from pydantic import BaseModel

from weather_forecast_collection.helpers import to_camel

#### ---- Models ---- ####


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

ACCU_CACHE = Path("accuweather-cache.pkl")


def get_cache_dict() -> Dict[str, Any]:
    if not ACCU_CACHE.exists():
        return dict()
    with open(ACCU_CACHE, "rb") as f:
        return pickle.load(f)


def store_cache_dict(d: Dict[str, Any]) -> None:
    with open(ACCU_CACHE, "wb") as f:
        pickle.dump(d, f)


def cache(func: Callable) -> Any:

    cache_dict = get_cache_dict()

    def cache_wrapper(*args, **kwargs):
        key = "[" + func.__name__ + "]"
        for arg in args:
            key += str(hash(arg)) + "_"
        for k, v in kwargs.items():
            key += str(hash(k)) + ":" + str(hash(v)) + "_"

        cached_value = cache_dict.get(key)
        if cached_value is not None:
            return cached_value

        val = func(*args, **kwargs)
        cache_dict[key] = val
        store_cache_dict(cache_dict)
        return val

    return cache_wrapper


@cache
def get_location_key(lat: float, long: float, api_key: str) -> str:
    base_url = (
        "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search?"
    )
    response = requests.get(base_url + f"apikey={api_key}&q={lat},{long}&details=true")
    if response.status_code == 200:
        return response.json()["Key"]
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        raise Exception("Error requesting location data from Accuweather.")


def tidy_current_condition(data: Dict[str, Any]) -> AccuConditions:
    return AccuConditions(**data)


def get_current_conditions(loc_key: str, api_key: str) -> AccuConditions:
    base_url = f"http://dataservice.accuweather.com/currentconditions/v1/{loc_key}?"
    response = requests.get(base_url + f"apikey={api_key}&details=true")
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


def get_five_day_forecast(loc_key: str, api_key: str) -> AccuFiveDayForecast:
    base_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{loc_key}?"
    response = requests.get(base_url + f"apikey={api_key}&details=true")
    if response.status_code == 200:
        return tidy_five_day_forecast(response.json())
    else:
        print(f"Error: {response.status_code}")
        print(response.json())
        raise Exception("Error requesting forecast data from Accuweather.")


def tidy_hour_forecast(data: List[Dict[str, Any]]) -> AccuTwelveHourForecast:
    return AccuTwelveHourForecast(periods=[AccuHourForecast(**d) for d in data])


def get_twelve_hour_forecast(loc_key: str, api_key: str) -> AccuTwelveHourForecast:
    base_url = (
        f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{loc_key}?"
    )
    response = requests.get(base_url + f"apikey={api_key}&details=true")
    if response.status_code == 200:
        # pprint(response.json())
        return tidy_hour_forecast(response.json())
        return None
    else:
        print(f"Error: {response.status_code}")
        pprint(response.json())
        raise Exception("Error requesting hourly forecast data from Accuweather.")


def get_accuweather_forecast(lat: float, long: float, api_key: str) -> AccuForecast:
    location = get_location_key(lat=lat, long=long, api_key=api_key)
    conditions = get_current_conditions(loc_key=location, api_key=api_key)
    daily_forecast = get_five_day_forecast(loc_key=location, api_key=api_key)
    hourly_forecast = get_twelve_hour_forecast(loc_key=location, api_key=api_key)
    return AccuForecast(
        datetime=datetime.now(),
        conditions=conditions,
        five_day=daily_forecast,
        hourly=hourly_forecast,
    )
