import os
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
from datetime import datetime, date
from weather import get_weather
from forecast import get_forecast

load_dotenv()

app = Flask(__name__, template_folder='templates')

# Get API key from environment variable
API_KEY = os.environ.get("API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            return redirect(url_for("weather", city=city))
    return render_template("index.html")

@app.route("/weather/<city>")
def weather(city):
    weather_api_data = get_weather(API_KEY, city)
    weather_data = None
    if weather_api_data and weather_api_data.get("cod") == 200:
        weather_data = {
            "city": weather_api_data["name"],
            "country": weather_api_data["sys"]["country"],
            "temperature": weather_api_data["main"]["temp"],
            "feels_like": weather_api_data["main"]["feels_like"],
            "description": weather_api_data["weather"][0]["description"],
            "humidity": weather_api_data["main"]["humidity"],
            "wind_speed": weather_api_data["wind"]["speed"],
            "icon": weather_api_data["weather"][0]["icon"],
        }
    return render_template("weather.html", weather_data=weather_data, city=city)

@app.route("/forecast/<city>")
def forecast(city):
    forecast_api_data = get_forecast(API_KEY, city)
    forecast_data = None
    if forecast_api_data and forecast_api_data.get("cod") == "200":
        daily_forecasts = {}
        today = date.today().strftime("%Y-%m-%d")
        for item in forecast_api_data.get("list", []):
            forecast_date = item["dt_txt"].split(" ")[0]
            if forecast_date == today:
                continue
            if forecast_date not in daily_forecasts:
                daily_forecasts[forecast_date] = {
                    "day": datetime.strptime(forecast_date, "%Y-%m-%d").strftime("%A"),
                    "temp_min": item["main"]["temp_min"],
                    "temp_max": item["main"]["temp_max"],
                    "description": item["weather"][0]["description"],
                    "icon": item["weather"][0]["icon"],
                }
            else:
                daily_forecasts[forecast_date]["temp_min"] = min(daily_forecasts[forecast_date]["temp_min"], item["main"]["temp_min"])
                daily_forecasts[forecast_date]["temp_max"] = max(daily_forecasts[forecast_date]["temp_max"], item["main"]["temp_max"])

        forecast_data = list(daily_forecasts.values())[:5]
    return render_template("forecast.html", forecast_data=forecast_data, city=city)

@app.route("/hourly-forecast/<city>")
def hourly_forecast(city):
    forecast_api_data = get_forecast(API_KEY, city)
    hourly_forecast_data = None
    if forecast_api_data and forecast_api_data.get("cod") == "200":
        hourly_forecast_data = []
        for item in forecast_api_data.get("list", [])[:8]:
            hourly_forecast_data.append({
                "time": datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%a, %I:%M %p"),
                "temp": item["main"]["temp"],
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"],
            })
    return render_template("hourly_forecast.html", hourly_data=hourly_forecast_data, city=city)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

def main():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    main()
