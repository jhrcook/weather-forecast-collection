#!/usr/bin/env python3

"""Collect forecast data from the OpenWeatherMap API."""

from datetime import datetime
from pprint import pprint
from typing import Any, Dict, List

import requests
from pydantic import BaseModel

#### ---- Models ---- ####


class WeatherSummary(BaseModel):
    description: str
    main: str


class OWMWeather(BaseModel):
    datetime: datetime
    clouds: float
    weather: WeatherSummary
    wind_speed: float

    def __init__(self, **data):
        data["datetime"] = data["dt"]
        data["weather"] = data["weather"][0]
        super().__init__(**data)


class OWMWeatherCurrent(OWMWeather):
    temp: float
    feels_like: float
    visibility: float
    wind_speed: float


class OWMWeatherHourly(OWMWeatherCurrent):
    prob_of_precipitation: float

    def __init__(self, **data):
        data["prob_of_precipitation"] = data["pop"]
        super().__init__(**data)


class OWMWeatherDaily(OWMWeather):
    prob_of_precipitation: float
    temp: Dict[str, float]
    feels_like: Dict[str, float]

    def __init__(self, **data):
        data["prob_of_precipitation"] = data["pop"]
        super().__init__(**data)


class OWMForecast(BaseModel):
    datetime: datetime
    current: OWMWeatherCurrent
    hourly: List[OWMWeatherHourly]
    daily: List[OWMWeatherDaily]

    def __str__(self) -> str:
        msg = "OpenWeatherMap Forecast\n"
        msg += " (collected at " + self.datetime.strftime("%y-%m-%d %H:%M") + ")\n"
        msg += f" forecasts for {len(self.hourly)} hours and {len(self.daily)} days plus the current conditions"
        return msg


#### ---- Data cleaning ---- ####


def tidy_current_forecast(data: Dict[str, Any]) -> OWMWeatherCurrent:
    return OWMWeatherCurrent(**data)


def tidy_hourly_forecast(data: List[Dict[str, Any]]) -> List[OWMWeatherHourly]:
    return [OWMWeatherHourly(**d) for d in data]


def tidy_daily_forecast(data: List[Dict[str, Any]]) -> List[OWMWeatherDaily]:
    return [OWMWeatherDaily(**d) for d in data]


def tidy_owm_onecall_data(data: Dict[str, Any]) -> OWMForecast:
    return OWMForecast(
        datetime=datetime.now(),
        current=tidy_current_forecast(data["current"]),
        hourly=tidy_hourly_forecast(data["hourly"]),
        daily=tidy_daily_forecast(data["daily"]),
    )


#### ---- Methods ---- ####


def get_current_weather(city: str, state: str, country: str, api_key: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{state},{country}&appid={api_key}&units=metric"
    response = requests.get(url)
    pprint(response.json())


def get_onecall_data(lat: float, long: float, api_key: str) -> OWMForecast:
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={long}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return tidy_owm_onecall_data(response.json())
    else:
        print(f"Error ({response.status_code})")
        print(response.json())
        raise Exception("Unable to get OpenWeatherMap data.")


#### ---- Main ---- ####


def get_openweathermap_data(lat: float, long: float, api_key: str):
    return get_onecall_data(lat=lat, long=long, api_key=api_key)
