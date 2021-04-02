#!/usr/bin/env python3

"""Collect forecast data from the ClimaCell API."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

import requests
from pydantic import BaseModel
from requests.exceptions import HTTPError


class TimeSteps(str, Enum):
    best = "best"
    oneDay = "1d"
    oneHour = "1h"
    thirtyMin = "30m"
    fifteenMin = "15m"
    fiveMin = "5m"
    oneMin = "1m"
    current = "current"


CLIMACELL_DATA_FIELDS = [
    "temperature",
    "temperatureApparent",
    "precipitationIntensity",
    "precipitationProbability",
    "precipitationType",
    "visibility",
    "cloudCover",
    "weatherCode",
    "humidity",
    "windSpeed",
]


class CCWeatherCode(int, Enum):
    unknown = 0
    clear = 1000
    cloudy = 1001
    mostly_clear = 1100
    partly_cloudy = 1101
    mostly_cloudy = 1102
    fog = 2000
    light_fog = 2100
    light_wind = 3000
    wind = 3001
    strong_wind = 3002
    drizzle = 4000
    rain = 4001
    light_rain = 4200
    heavy_rain = 4201
    snow = 5000
    flurries = 5001
    light_snow = 5100
    heavy_snow = 5101
    freezing_drizzle = 6000
    freezing_rain = 6001
    light_freezing_rain = 6200
    heavy_freezing_rain = 6201
    ice_pellets = 7000
    heavy_ice_pellets = 7101
    light_ice_pellets = 7102
    thunderstorm = 8000


class CCDataValues(BaseModel):
    temperature: float
    temperatureApparent: float
    precipitationIntensity: float
    precipitationProbability: float
    precipitationType: float
    visibility: float
    cloudCover: float
    weatherCode: CCWeatherCode
    humidity: float
    windSpeed: float


class CCData(BaseModel):
    startTime: datetime
    values: CCDataValues


class CCTimeline(BaseModel):
    startTime: datetime
    endTime: datetime
    timestep: TimeSteps
    intervals: List[CCData]


class CCForecastData(BaseModel):
    version: int = 1
    timestamp: datetime
    current: CCTimeline
    oneHour: CCTimeline
    oneDay: CCTimeline

    def __str__(self) -> str:
        msg = "ClimaCell Forecast Data\n"
        msg += f"  collected {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
        msg += f"  {len(self.current.intervals)} measures of current weather\n"
        msg += f"  {len(self.oneHour.intervals)} measures at 1 hour intervals\n"
        msg += f"  {len(self.oneDay.intervals)} measures at 1 day intervals\n"
        return msg


def tidy_timeline(data: List[Dict[str, Any]]) -> CCForecastData:
    return CCForecastData(
        timestamp=datetime.now(timezone.utc),
        current=CCTimeline(**data[0]),
        oneHour=CCTimeline(**data[1]),
        oneDay=CCTimeline(**data[2]),
    )


CLIMACELL_DATA_TIMESTEPS = ["current", "1h", "1d"]


def get_climacell_data(lat: float, long: float, api_key: str) -> CCForecastData:
    url = "https://data.climacell.co/v4/timelines"
    querystring = {
        "fields": CLIMACELL_DATA_FIELDS,
        "location": f"{lat},{long}",
        "timesteps": CLIMACELL_DATA_TIMESTEPS,
        "units": "metric",
        "apikey": api_key,
    }
    response = requests.get(url, params=querystring)
    if response.status_code == 200:
        return tidy_timeline(response.json()["data"]["timelines"])
    else:
        raise HTTPError(response=response)
