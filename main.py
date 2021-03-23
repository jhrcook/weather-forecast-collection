#!/usr/bin/env python3

import json
from datetime import datetime
from pathlib import Path
from pprint import pprint
from typing import Callable

import requests_cache
from pydantic.main import BaseModel

import coordinates as coord
from apis import accuweather_api as accu
from apis import climacell_api as cc
from apis import national_weather_service_api as nws
from apis import openweathermap_api as owm

# requests_cache.install_cache("dev-cache.sqlite", backend="sqlite", expire_after=86400)

DATA_DIR = Path("data")
if not DATA_DIR.exists():
    DATA_DIR.mkdir()


def fmt_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def make_filepath(source: str) -> Path:
    return DATA_DIR / f"{source}_{fmt_date(datetime.now())}.json"


def save_data(source: str, data: BaseModel) -> Path:
    file_path = make_filepath(source=source)
    with open(file_path, "w") as json_file:
        json.dump(data.json(), json_file)
    return file_path


def read_data(fp: Path, model: Callable):
    with open(fp) as json_file:
        return model(**json.loads(json.load(json_file)))


if __name__ == "__main__":
    nws_forecast = nws.get_nsw_forecast(coord.LATITUDE, coord.LONGITUDE)
    fp = save_data("national-weather-service", nws_forecast)
    stored_forecast = read_data(fp, nws.NSWForecast)
    print(type(stored_forecast))
    # accu_forecast = accu.get_accuweather_forecast(
    #     lat=coord.LATITUDE, long=coord.LONGITUDE
    # )
    # owm_forecast = owm.get_openweathermap_data(lat=coord.LATITUDE, long=coord.LONGITUDE)
    # climacell_forecast = cc.get_climacell_data(lat=coord.LATITUDE, long=coord.LONGITUDE)

    # TODO: Store data.
    # Probably easiest to just write each to a separate JSON file with the name "{source}-{timestamp}.json".

    # TODO: GitHub Action to run script and store data.
