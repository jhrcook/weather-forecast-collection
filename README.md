# Weather Forecast Collection

[![python](https://img.shields.io/badge/Python-3.9-3776AB.svg?style=flat&logo=python)](https://www.python.org)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![License: GPLv3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A collection of weather forecasts and nowcasts.

## Install

```bash
pip install git+https://github.com/jhrcook/weather_forecast_collection.git
```

## Quickstart

(In progress.)

### AccuWeather

```python
from weather_forecast_collection.apis import accuweather_api

data = get_accuweather_forecast(lat=latitude, long=longitude, api_key=ACCU_KEY)
```

## Sources

### AccuWeather (done)

- https://developer.accuweather.com/apis
- https://developer.accuweather.com/accuweather-current-conditions-api/apis
- https://developer.accuweather.com/accuweather-forecast-api/apis

### The Weather Company (The Weather Channel)

From what I can tell, this API used to be open, but is now only available to
individuals with a "personal weather station" linked with Weather Underground.

- https://weather.com/swagger-docs/call-for-code

### National Weather Service (done)

- https://www.weather.gov/documentation/services-web-api
- https://weather-gov.github.io/api/

### Yahoo Weather (skip)

A banner on the documentation website indicates that this API will be closed soon.

> On approximately May 1, 2021, the free Yahoo Weather API will be retired and will cease to function. Unfortunately, we will not be offering a replacement API, and there will be no paid alternative.

- https://developer.yahoo.com/weather/documentation.html

### Dark Sky

The API is no longer open, but I may try to webscrape the HTML or use RapidAPI.

- https://darksky.net
- https://rapidapi.com/darkskyapis/api/dark-sky

### ClimaCell (done)

- https://www.climacell.co/weather-api/

### OpenWeatherMap (done)

- https://openweathermap.org/api
