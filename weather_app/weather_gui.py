import os
import tkinter as tk
from tkinter import ttk, messagebox
import requests
from dotenv import load_dotenv

API_URL = "https://api.openweathermap.org/data/2.5/weather"


def fetch(city, units):
    api_key = os.getenv("OWM_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OWM_API_KEY. Put it in .env or environment.")
    r = requests.get(
        API_URL, params={"q": city, "appid": api_key, "units": units}, timeout=10
    )
    if r.status_code == 401:
        raise RuntimeError("Unauthorized: invalid API key.")
    if r.status_code == 404:
        raise RuntimeError(f"City not found: {city}")
    r.raise_for_status()
    return r.json()


def on_search():
    city = city_var.get().strip()
    units = units_var.get()
    if not city:
        messagebox.showwarning("Warning", "Please enter a city name.")
        return
    try:
        data = fetch(city, units)
        name = data.get("name", "")
        country = (data.get("sys") or {}).get("country", "")
        main = data.get("main", {})
        wind = data.get("wind", {})
        weather = (data.get("weather") or [{}])[0]

        temp = main.get("temp")
        hum = main.get("humidity")
        wind_speed = wind.get("speed")
        cond = str(weather.get("description", "")).title()

        unit_temp = "°C" if units == "metric" else "°F"
        unit_wind = "m/s" if units == "metric" else "mph"

        result = (
            f"{name}, {country}\n"
            f"{cond}\n"
            f"Temp: {temp}{unit_temp}\n"
            f"Humidity: {hum}%\n"
            f"Wind: {wind_speed} {unit_wind}"
        )
        output_var.set(result)
    except requests.exceptions.Timeout:
        messagebox.showerror("Error", "Request timed out.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("HTTP Error", str(e))
    except RuntimeError as e:
        messagebox.showerror("Config Error", str(e))


# Bootstrap
load_dotenv()

root = tk.Tk()
root.title("WeatherApp")
root.geometry("380x260")
root.resizable(False, False)

frm = ttk.Frame(root, padding=12)
frm.pack(fill="both", expand=True)

ttk.Label(frm, text="City").grid(row=0, column=0, sticky="w")
city_var = tk.StringVar(value="Ho Chi Minh")
ttk.Entry(frm, textvariable=city_var, width=26).grid(
    row=0, column=1, columnspan=2, sticky="we"
)

ttk.Label(frm, text="Units").grid(row=1, column=0, sticky="w")
units_var = tk.StringVar(value="metric")
ttk.Radiobutton(frm, text="Metric (°C)", variable=units_var, value="metric").grid(
    row=1, column=1, sticky="w"
)
ttk.Radiobutton(frm, text="Imperial (°F)", variable=units_var, value="imperial").grid(
    row=1, column=2, sticky="w"
)

ttk.Button(frm, text="Search", command=on_search).grid(
    row=2, column=0, columnspan=3, pady=8, sticky="we"
)

output_var = tk.StringVar()
out = ttk.Label(frm, textvariable=output_var, anchor="w", justify="left")
out.grid(row=3, column=0, columnspan=3, sticky="we")

for i in range(3):
    frm.columnconfigure(i, weight=1)

root.mainloop()
