import json

import requests

from Constants import *


def send_location(recipient_id, text):
    payload = {}
    payload["recipient"]={"id":recipient_id}
    payload["message"] = {"text": text,
                            "quick_replies":[{
                                "content_type":"location"
                            }]
                        }
    r = requests.post(FACEBOOK_URL,
                    params={"access_token": FACEBOOK_TOKEN},
                    data=json.dumps(payload),
                    headers={'Content-type': 'application/json'})
