import os

from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(file_name: str):
    return open(os.path.join(os.path.dirname(__file__), file_name)).read()


setup(
    name="weather_forecast_collection",
    version="0.1.5",
    author="Joshua Cook",
    description=("Simple wrappers for several open weather APIs."),
    license="BSD",
    keywords="weather forecast API data collection",
    url="https://github.com/jhrcook/weather_forecast_collection",
    project_urls={
        "Issue Tracker": "https://github.com/jhrcook/weather_forecast_collection/issues",
    },
    packages=["weather_forecast_collection", "weather_forecast_collection.apis"],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ],
    install_requires=["requests", "pydantic"],
)
