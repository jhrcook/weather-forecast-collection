#!/usr/bin/env python3

"""Collect forecast data from the National Weather Service API."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from pydantic import BaseModel, HttpUrl


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


class NSWSevenDayForecast(BaseModel):
    periods: List[NWSPeriodForecast]


class NSWHourlyForecast(BaseModel):
    updated: datetime
    forecast_generator: str
    generated_at: datetime
    periods: List[NWSPeriodForecast]


class NSWForecast(BaseModel):
    seven_day: NSWSevenDayForecast
    hourly_forecast: NSWHourlyForecast


def get_grid_points(lat: float, long: float) -> Dict[Any, Any]:
    response = requests.get(f"https://api.weather.gov/points/{lat},{long}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"error: {response.status_code}")
        print(response.json())
        raise Exception("Failed request.")


def get_grid_coords(lat: float, long: float) -> Tuple[int, int]:
    grid_data = get_grid_points(lat=lat, long=long)
    props = grid_data["properties"]
    return props["gridX"], props["gridY"]


def extract_period_data(res: requests.Response) -> List[NWSPeriodForecast]:
    period_data = res.json()["properties"]["periods"]
    return [NWSPeriodForecast(**d) for d in period_data]


def get_seven_day_forecast(grid_x: int, grid_y: int) -> NSWSevenDayForecast:
    response = requests.get(
        f"https://api.weather.gov/gridpoints/BOX/{grid_x},{grid_y}/forecast"
    )
    if response.status_code == 200:
        return NSWSevenDayForecast(periods=extract_period_data(response))
    else:
        print(f"Error ({response.status_code})")
        print(response.json()["detail"])
        raise Exception("Error retriving National Weather Service forecast.")


def build_hourly_forecast(res: requests.Response) -> NSWHourlyForecast:
    props = res.json()["properties"]
    return NSWHourlyForecast(
        updated=props["updated"],
        forecast_generator=props["forecastGenerator"],
        generated_at=props["generatedAt"],
        periods=extract_period_data(res),
    )


def get_hourly_forecast(grid_x: int, grid_y: int) -> NSWHourlyForecast:
    response = requests.get(
        f"https://api.weather.gov/gridpoints/BOX/{grid_x},{grid_y}/forecast/hourly"
    )
    if response.status_code == 200:
        return build_hourly_forecast(response)
    else:
        print(f"Error ({response.status_code})")
        print(response.json()["detail"])
        raise Exception("Error retriving National Weather Service hourly forecast.")


def get_nsw_forecast(lat: float, long: float) -> NSWForecast:
    grid_x, grid_y = get_grid_coords(lat=lat, long=long)
    seven_day = get_seven_day_forecast(grid_x=grid_x, grid_y=grid_y)
    hourly_forecast = get_hourly_forecast(grid_x=grid_x, grid_y=grid_y)
    return NSWForecast(seven_day=seven_day, hourly_forecast=hourly_forecast)
