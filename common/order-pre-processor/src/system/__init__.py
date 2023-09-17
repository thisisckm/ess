import requests
import json


class TeamsWebhookException(Exception): ...

def post_message(url, message: str) -> None:
    payload = {"text": message}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code != 200:
        raise TeamsWebhookException(response.reason)
