import requests
from django.conf import settings


def send_afro_otp(user):
    url = "https://api.afromessage.com/api/send"

    headers = {
        "Authorization": f"Bearer {settings.AFRO_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {

        "from":settings.AFRO_SENDER_ID,
        "to": user.phone,
        "message": f"Your OTP code is {user.otp}"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        # Log response for debugging
        print("AfroMessage raw response:", response.text)

        if response.status_code == 200 :
            response_data=response.json()
            if response_data.get('acknowledge')=='success':
                return {
                    "success": True,
                    "message_id":response_data['response'].get('message_id'),
                    "status":response_data['response'].get('status','Send in progress'),
                }
            else:
                return {"success": False, "error": response_data.get('response', {}).get('errors', 'Unknown error')}
        else:
            return {"success": False, "error": f"Error {response.status_code}: {response.text}"}

    except requests.RequestException as e:
        return {"success": False, "error": str(e)}
