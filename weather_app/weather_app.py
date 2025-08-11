#!/usr/bin/env python3
import os, sys, argparse
import requests
from dotenv import load_dotenv

API_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch_weather(city: str, units: str = "metric") -> dict:
    api_key = os.getenv("OWM_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OWM_API_KEY. Put it in .env or your environment.")
    r = requests.get(
        API_URL, params={"q": city, "appid": api_key, "units": units}, timeout=10
    )
    if r.status_code == 401:
        raise RuntimeError("Unauthorized: invalid API key.")
    if r.status_code == 404:
        raise RuntimeError(f"City not found: {city}")
    r.raise_for_status()
    return r.json()


def format_report(data: dict, units: str) -> str:
    name = data.get("name", "")
    sysc = data.get("sys", {})
    country = sysc.get("country", "")
    main = data.get("main", {})
    wind = data.get("wind", {})
    weather = (data.get("weather") or [{}])[0]

    temp = main.get("temp")
    hum = main.get("humidity")
    wind_speed = wind.get("speed")
    cond = weather.get("description", "").title()

    unit_temp = "°C" if units == "metric" else "°F"
    unit_wind = "m/s" if units == "metric" else "mph"

    return (
        f"Location : {name}, {country}\n"
        f"Condition: {cond}\n"
        f"Temp     : {temp}{unit_temp}\n"
        f"Humidity : {hum}%\n"
        f"Wind     : {wind_speed} {unit_wind}\n"
    )


def main():
    load_dotenv()  # load .env if exists
    p = argparse.ArgumentParser(description="Simple Weather CLI using OpenWeatherMap")
    p.add_argument("city", nargs="+", help="City name, e.g. London or 'Ho Chi Minh'")
    p.add_argument(
        "-u",
        "--units",
        choices=["metric", "imperial"],
        default="metric",
        help="Units system",
    )
    args = p.parse_args()
    city = " ".join(args.city)

    try:
        data = fetch_weather(city, units=args.units)
        print(format_report(data, args.units))
    except requests.exceptions.Timeout:
        print("Error: Request timed out.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
