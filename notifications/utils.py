import requests
import json
from django.conf import settings

def send_push_notification(token, title, body, data=None):
    """
    Send a push notification using Firebase Cloud Messaging (FCM).

    Args:
        token (str): The device token to send the notification to.
        title (str): The notification title.
        body (str): The notification body.
        data (dict, optional): Additional data to send with the notification.

    Returns:
        response (requests.Response): The response from the FCM server.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"key={settings.FCM_SERVER_KEY}",
    }

    payload = {
        "to": token,
        "notification": {
            "title": title,
            "body": body,
        },
        "data": data or {},
    }

    response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(payload))
    return response
