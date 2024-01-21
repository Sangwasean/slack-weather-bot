import os
import json
import requests
from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slackeventsapi import SlackEventAdapter
from flask import Flask, request
from datetime import datetime,timedelta


load_dotenv()
app = Flask(__name__)

slack_token =os.getenv("BOTAUTHUSERTOKEN")
openweather_api_key =os.getenv("OPENWEATHERMAPAPIKEY")
slack_signing_secret = os.getenv("SIGNINGSECRET")

slack_event_adapter=SlackEventAdapter(slack_signing_secret,'/slack/events',app)
client = WebClient(token=slack_token)
BOT_ID=client.api_call("auth.test")['user_id']
SCHEDULED_MESSAGE=[
    {'text':"ss",'post_at':(datetime.now(),timedelta(seconds=10)).timestamp(),'channel':"C06EMNHAKNW"}
]

@slack_event_adapter.on('app_mention')
def message(payload):
    event=payload.get('event',{})
    channel_id=event.get('channel')
    text=event.get('text')
    user_id=event.get('user')
    sender_name = f"<@{user_id}>"
    if BOT_ID != user_id:
                client.chat_postMessage(channel=channel_id, text=f"HEY :wave: {sender_name} \nFor more information text sean ")

def get_weather(nyabihu):
    api_url = f"api.openweathermap.org/data/2.5/forecast?lat=1.6955&lon=29.5572&appid=openweather_api_key"
    response = requests.get(api_url)
    data = response.json()
    return data


def format_weather_message(weather_data):
    main_weather = weather_data["weather"][0]["main"]
    description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]

    message = f"The weather is {main_weather} ({description}) with a temperature of {temperature}°C."
    return message


def send_weather_message(messages):
    ids=[]
    for msg in messages:
        response=client.chat_scheduleMessage(channel=msg['channel'],text=msg['channel'],post_at=msg['post_At'])
        id_=response.get('id')
        ids.append(id_)


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
