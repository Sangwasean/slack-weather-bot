import requests
import os

def get_weather(api_key, city):
    api_key = os.environ.get('OPENWEATHERMAP_API_KEY')
    if not api_key:
        raise ValueError("API key not found in environment variables")
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if data["cod"] == "404":
            return {"error": "City not found"}

        weather_info = {
            "description": data["weather"][0]["description"],
            "temperature": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }

        return weather_info

    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching data: {e}"}
