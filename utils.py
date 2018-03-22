import configparser
import json
import re
import urllib2

import requests
from bs4 import BeautifulSoup

from Constants import *

###################    Read configuration    ####################
config = configparser.ConfigParser()
config.read('keys.ini')
TOKEN_1 = config['google']['TOKEN_1']


def send_location(recipient_id, text):
    payload = {}
    payload["recipient"] = {"id": recipient_id}
    payload["message"] = {
        "text":
        text,
        "quick_replies": [{
            "content_type": "location"
        }, {
            "content_type": "text",
            "title": "No",
            "payload": "No"
        }]
    }
    r = requests.post(
        FACEBOOK_URL,
        params={"access_token": FACEBOOK_TOKEN},
        data=json.dumps(payload),
        headers={
            'Content-type': 'application/json'
        })


def aux_parse_url_to_text(text):
    text = text.replace("%C3%A1", "a")
    text = text.replace("%C3%A9", "e")
    text = text.replace("%C3%AD", "i")
    text = text.replace("%C3%B3", "o")
    text = text.replace("%C3%BA", "u")
    text = re.sub(r'%[A-Z|0-9]{2}', '', text)
    text = re.sub(r'[0-9]', '', text)
    text = re.sub(r'[+]+', '+', text)
    return text


def parse_response(text):
    #Check if is a url
    is_url = 'https://l.facebook.com' in text
    if is_url:
        #Now parse url,
        text = urllib2.unquote(text)
        lat_lon = text.split("where1=")[1].split("&")[0].replace("%2C+", "%")
        lat = lat_lon.split("%")[0]
        lon = lat_lon.split("%")[-1]
        try:
            lat = float(lat)
            lon = float(lon)
            url = GOOGLE_LATLON % (lat, lon, TOKEN_1)
            page = requests.get(url).json()["results"]
        except ValueError:
            lat_lon = aux_parse_url_to_text(lat_lon)
            url = GOOGLE_ADDRESS + lat_lon + "&key=" + TOKEN_1
            page = requests.get(url).json()["results"]
        if page:
            components = page[0]["address_components"]
            state = [
                c["long_name"] for c in components
                if "administrative_area_level_1" in c["types"]
            ]
            mun = []
            level_3 = []
            localities = []
            for page_component in page:
                component = page_component["address_components"]
                mun += [
                    c["long_name"] for c in component
                    if "administrative_area_level_2" in c["types"]
                ]
                level_3 += [
                    c["long_name"] for c in component
                    if "administrative_area_level_3" in c["types"]
                ]
                localities += [
                    c["long_name"] for c in component
                    if "locality" in c["types"]
                ]

            if not mun:
                mun = level_3 if level_3 else localities

            state = state[0] if state else ""
            mun = mun[0] if mun else ""
            return {"edo": state, "mun": mun}
    return {"edo": "", "mun": ""}
