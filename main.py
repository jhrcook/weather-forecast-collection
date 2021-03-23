#!/usr/bin/env python3

from datetime import datetime
from pprint import pprint

import requests_cache

import coordinates as coord
from apis import accuweather_api as accu
from apis import climacell_api as cc
from apis import national_weather_service_api as nws
from apis import openweathermap_api as owm

requests_cache.install_cache("dev-cache.sqlite", backend="sqlite", expire_after=86400)


def fmt_date(dt: datetime) -> str:
    return dt.date().strftime("%m-%d")


if __name__ == "__main__":
    # nws_forecast: nws.NSWForecast = nws.get_nsw_forecast(
    #     coord.LATITUDE, coord.LONGITUDE
    # )

    # accu_forecast = accu.get_accuweather_forecast(
    #     lat=coord.LATITUDE, long=coord.LONGITUDE
    # )

    # owm_forecast = owm.get_openweathermap_data(lat=coord.LATITUDE, long=coord.LONGITUDE)
    # print(owm_forecast)

    climacell_forecast = cc.get_climacell_data(lat=coord.LATITUDE, long=coord.LONGITUDE)
    print(climacell_forecast)
