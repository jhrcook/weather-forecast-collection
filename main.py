#!/usr/bin/env python3

from datetime import datetime

import coordinates as coord
from apis import national_weather_service_api as nws


def fmt_date(dt: datetime) -> str:
    return dt.date().strftime("%m-%d")


if __name__ == "__main__":
    nws_forecast: nws.NSWForecast = nws.get_nsw_forecast(
        coord.LATITUDE, coord.LONGITUDE
    )
    print(len(nws_forecast.seven_day.periods))
    print(len(nws_forecast.hourly_forecast.periods))
    # for period in nws_forecast.seven_day:
    #     when = "day" if period.isDaytime else "night"
    # print(f"{fmt_date(period.startTime)} ({when}): {period.temperature} {period.temperatureUnit}")
