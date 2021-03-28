#!/usr/bin/env python3

"""Collect forecast data from the National Weather Service API."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from pydantic import BaseModel, HttpUrl
from requests.exceptions import HTTPError


class NWSPeriodForecast(BaseModel):
    detailedForecast: str
    shortForecast: str
    startTime: datetime
    endTime: datetime
    icon: HttpUrl
    isDaytime: bool
    name: str
    number: int
    temperature: float
    temperatureUnit: str
    temperatureTrend: Optional[str]
    windDirection: str
    windSpeed: str


class NWSSevenDayForecast(BaseModel):
    periods: List[NWSPeriodForecast]


class NWSHourlyForecast(BaseModel):
    updated: datetime
    forecast_generator: str
    generated_at: datetime
    periods: List[NWSPeriodForecast]


class NWSForecast(BaseModel):
    timestamp: datetime
    seven_day: NWSSevenDayForecast
    hourly_forecast: NWSHourlyForecast


def get_grid_points(lat: float, long: float) -> Dict[Any, Any]:
    response = requests.get(f"https://api.weather.gov/points/{lat},{long}")
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPError(response=response)


def get_grid_coords(lat: float, long: float) -> Tuple[int, int]:
    grid_data = get_grid_points(lat=lat, long=long)
    props = grid_data["properties"]
    return props["gridX"], props["gridY"]


def extract_period_data(res: requests.Response) -> List[NWSPeriodForecast]:
    period_data = res.json()["properties"]["periods"]
    return [NWSPeriodForecast(**d) for d in period_data]


def get_seven_day_forecast(grid_x: int, grid_y: int) -> NWSSevenDayForecast:
    response = requests.get(
        f"https://api.weather.gov/gridpoints/BOX/{grid_x},{grid_y}/forecast"
    )
    if response.status_code == 200:
        return NWSSevenDayForecast(periods=extract_period_data(response))
    else:
        raise HTTPError(response=response)


def build_hourly_forecast(res: requests.Response) -> NWSHourlyForecast:
    props = res.json()["properties"]
    return NWSHourlyForecast(
        updated=props["updated"],
        forecast_generator=props["forecastGenerator"],
        generated_at=props["generatedAt"],
        periods=extract_period_data(res),
    )


def get_hourly_forecast(grid_x: int, grid_y: int) -> NWSHourlyForecast:
    response = requests.get(
        f"https://api.weather.gov/gridpoints/BOX/{grid_x},{grid_y}/forecast/hourly"
    )
    if response.status_code == 200:
        return build_hourly_forecast(response)
    else:
        raise HTTPError(response=response)


def get_nws_forecast(lat: float, long: float) -> NWSForecast:
    grid_x, grid_y = get_grid_coords(lat=lat, long=long)
    seven_day = get_seven_day_forecast(grid_x=grid_x, grid_y=grid_y)
    hourly_forecast = get_hourly_forecast(grid_x=grid_x, grid_y=grid_y)
    return NWSForecast(
        timestamp=datetime.now(), seven_day=seven_day, hourly_forecast=hourly_forecast
    )
