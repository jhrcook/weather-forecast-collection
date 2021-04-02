#!/usr/bin/env python3

"""Collect forecast data from the OpenWeatherMap API."""

from datetime import datetime
from typing import Any, Dict, List

import requests
from pydantic import BaseModel
from requests.exceptions import HTTPError

#### ---- Models ---- ####


class WeatherSummary(BaseModel):
    description: str
    main: str


class OWMWeather(BaseModel):
    dt: datetime
    clouds: float
    weather: WeatherSummary
    wind_speed: float

    def __init__(self, **data):
        if isinstance(data["weather"], list):
            data["weather"] = data["weather"][0]
        super().__init__(**data)


class OWMWeatherCurrent(OWMWeather):
    temp: float
    feels_like: float
    visibility: float
    wind_speed: float


class OWMWeatherHourly(OWMWeatherCurrent):
    pop: float


class OWMWeatherDaily(OWMWeather):
    pop: float
    temp: Dict[str, float]
    feels_like: Dict[str, float]


class OWMForecast(BaseModel):
    version: int = 1
    timestamp: datetime
    current: OWMWeatherCurrent
    hourly: List[OWMWeatherHourly]
    daily: List[OWMWeatherDaily]

    def __str__(self) -> str:
        msg = "OpenWeatherMap Forecast\n"
        msg += " (collected at " + self.timestamp.strftime("%y-%m-%d %H:%M") + ")\n"
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
        timestamp=datetime.now(),
        current=tidy_current_forecast(data["current"]),
        hourly=tidy_hourly_forecast(data["hourly"]),
        daily=tidy_daily_forecast(data["daily"]),
    )


#### ---- Methods ---- ####


# def get_current_weather(city: str, state: str, country: str, api_key: str):
#     url = f"http://api.openweathermap.org/data/2.5/weather?q={city},{state},{country}&appid={api_key}&units=metric"
#     response = requests.get(url)
# pprint(response.json())


def get_onecall_data(lat: float, long: float, api_key: str) -> OWMForecast:
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={long}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return tidy_owm_onecall_data(response.json())
    else:
        raise HTTPError(response=response)


#### ---- Main ---- ####


def get_openweathermap_data(lat: float, long: float, api_key: str):
    return get_onecall_data(lat=lat, long=long, api_key=api_key)
