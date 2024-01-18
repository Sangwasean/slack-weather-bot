import os
import json
import requests
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from flask import Flask, request

load_dotenv()
app = Flask(__name__)
slack_token =os.getenv("BOTAUTHUSERTOKEN")
openweather_api_key =os.getenv("OPENWEATHERMAPAPIKEY")
slack_signing_secret = os.getenv("SIGNINGSECRET")
client = WebClient(token=slack_token)


def get_weather(city):
    api_url = f"api.ope1nweathermap.org/data/2.5/forecast?lat=1.6955&lon=29.5572&appid=openweather_api_key"
    response = requests.get(api_url)
    data = response.json()
    return data


def format_weather_message(weather_data):
    main_weather = weather_data["weather"][0]["main"]
    description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]

    message = f"The weather is {main_weather} ({description}) with a temperature of {temperature}°C."
    return message


def send_weather_message(channel_id, message):
    try:
        client.chat_postMessage(channel=channel_id, text=message)
    except SlackApiError as e:
        print(f"Error posting message to Slack: {e.response['error']}")


@app.route("/slack/events", methods=["POST"])
def slack_events():
    try:
        data = json.loads(request.data.decode("utf-8"))
        if "challenge" in data:
            return data["challenge"]

        event = data["event"]
        if "text" in event and event["text"].startswith("!weather"):
            city = event["text"].split(" ", 1)[1]

            weather_data = get_weather(city)

            message = format_weather_message(weather_data)

            send_weather_message(event["channel"], message)

        return "OK"
    except Exception as e:
        print(f"Error: {str(e)}")
        return "Internal Server Error", 500



if __name__ == "__main__":
    app.run(port=3000,debug=True)
