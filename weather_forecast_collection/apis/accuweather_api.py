#!/usr/bin/env python3

"""Collect forecast data from the Accuweather API."""

import pickle
from datetime import datetime, timezone
from pathlib import Path
from pprint import pprint
from typing import Any, Callable, Dict, List, Optional

import requests
from pydantic import BaseModel
from requests.exceptions import HTTPError

#### ---- Models ---- ####


class ValueUnit(BaseModel):
    Value: float
    Unit: str


class MultimetricTemperature(BaseModel):
    Metric: ValueUnit
    Imperial: ValueUnit


class MinMaxTemperature(BaseModel):
    Minimum: ValueUnit
    Maximum: ValueUnit


class AccuConditions(BaseModel):
    LocalObservationDateTime: datetime
    WeatherText: str
    HasPrecipitation: bool
    Precipitation: Optional[str]
    IsDayTime: bool
    Temperature: MultimetricTemperature
    ApparentTemperature: MultimetricTemperature
    RealFeelTemperature: MultimetricTemperature
    RealFeelTemperatureShade: MultimetricTemperature
    RelativeHumidity: float
    CloudCover: float


class AccuSummary(BaseModel):
    IconPhrase: str
    HasPrecipitation: bool
    ShortPhrase: str
    LongPhrase: str
    PrecipitationProbability: float
    ThunderstormProbability: float
    RainProbability: float
    SnowProbability: float
    IceProbability: float
    TotalLiquid: ValueUnit
    Rain: ValueUnit
    Snow: ValueUnit
    Ice: ValueUnit
    HoursOfPrecipitation: float
    HoursOfRain: float
    HoursOfSnow: float
    HoursOfIce: float
    CloudCover: float


class AccuDayForecast(BaseModel):
    Date: datetime
    Temperature: MinMaxTemperature
    RealFeelTemperature: MinMaxTemperature
    RealFeelTemperatureShade: MinMaxTemperature
    Day: AccuSummary
    Night: AccuSummary


class AccuHourForecast(BaseModel):
    DateTime: datetime
    IsDaylight: bool
    Temperature: ValueUnit
    RealFeelTemperature: ValueUnit
    IconPhrase: str
    HasPrecipitation: bool
    PrecipitationProbability: float
    RainProbability: float
    SnowProbability: float
    IceProbability: float
    TotalLiquid: ValueUnit
    Rain: ValueUnit
    Snow: ValueUnit
    Ice: ValueUnit
    CloudCover: float


class AccuFiveDayForecast(BaseModel):
    EffectiveDate: datetime
    EndDate: Optional[datetime]
    DailyForecasts: List[AccuDayForecast]


class AccuTwelveHourForecast(BaseModel):
    Periods: List[AccuHourForecast]


class AccuForecast(BaseModel):
    version: int = 1
    timestamp: datetime
    conditions: AccuConditions
    fiveday: AccuFiveDayForecast
    hourly: AccuTwelveHourForecast

    def __str__(self):
        return f"Collected on {self.timestamp.strftime('%y-%m-%d %H:%M:%S')}"


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
        raise HTTPError(response=response)


def tidy_current_condition(data: Dict[str, Any]) -> AccuConditions:
    return AccuConditions(**data)


def get_current_conditions(loc_key: str, api_key: str) -> AccuConditions:
    base_url = f"http://dataservice.accuweather.com/currentconditions/v1/{loc_key}?"
    response = requests.get(base_url + f"apikey={api_key}&details=true")
    if response.status_code == 200:
        return tidy_current_condition(response.json()[0])
    else:
        raise HTTPError(response=response)


def tidy_five_day_forecast(data: Dict[str, Any]) -> AccuFiveDayForecast:
    return AccuFiveDayForecast(
        EffectiveDate=data["Headline"]["EffectiveDate"],
        EndDate=data["Headline"]["EndDate"],
        DailyForecasts=[AccuDayForecast(**d) for d in data["DailyForecasts"]],
    )


def get_five_day_forecast(loc_key: str, api_key: str) -> AccuFiveDayForecast:
    base_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{loc_key}?"
    response = requests.get(base_url + f"apikey={api_key}&details=true")
    if response.status_code == 200:
        return tidy_five_day_forecast(response.json())
    else:
        raise HTTPError(response=response)


def tidy_hour_forecast(data: List[Dict[str, Any]]) -> AccuTwelveHourForecast:
    return AccuTwelveHourForecast(Periods=[AccuHourForecast(**d) for d in data])


def get_twelve_hour_forecast(loc_key: str, api_key: str) -> AccuTwelveHourForecast:
    base_url = (
        f"http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/{loc_key}?"
    )
    response = requests.get(base_url + f"apikey={api_key}&details=true")
    if response.status_code == 200:
        return tidy_hour_forecast(response.json())
    else:
        raise HTTPError(response=response)


def get_accuweather_forecast(lat: float, long: float, api_key: str) -> AccuForecast:
    location = get_location_key(lat=lat, long=long, api_key=api_key)
    conditions = get_current_conditions(loc_key=location, api_key=api_key)
    daily_forecast = get_five_day_forecast(loc_key=location, api_key=api_key)
    hourly_forecast = get_twelve_hour_forecast(loc_key=location, api_key=api_key)
    return AccuForecast(
        timestamp=datetime.now(timezone.utc),
        conditions=conditions,
        fiveday=daily_forecast,
        hourly=hourly_forecast,
    )
