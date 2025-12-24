import requests
from django.conf import settings


def create_daily_room(room_name):
    url = "https://api.daily.co/v1/rooms"
    headers = {
        "Authorization": f"Bearer {settings.DAILY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "name": room_name,
        "properties": {
            "enable_chat": True,
            "enable_knocking": False,
            "start_audio_off": False,
            "start_video_off": False,
            "max_participants": 2
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()


def create_daily_token(room_name, is_owner=False):
    url = "https://api.daily.co/v1/meeting-tokens"
    headers = {
        "Authorization": f"Bearer {settings.DAILY_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "properties": {
            "room_name": room_name,
            "is_owner": is_owner
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["token"]
