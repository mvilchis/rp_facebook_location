import ast
import configparser
import json
import re
import sys
import calendar
from math import atan2, cos, radians, sin, sqrt
from urllib.request import unquote
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from fbmq import Page, Template

from Constants import *

###################    Read configuration    ####################
config = configparser.ConfigParser()
config.read('keys.ini')
google_tokens = [config["google"][k] for k in config["google"].keys()]

key_id = 0

def send_location(recipient_id, text):
    """
    Function to send location to facebook id, recipient_id

    :param recipient_id: <String> facebook identifier
    :param  text: <String> text to send to user
    """
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
    fb_tokens = [FACEBOOK_TOKEN_1, FACEBOOK_TOKEN_2, FACEBOOK_TOKEN_3]
    for token in fb_tokens:
        r = requests.post(
            FACEBOOK_URL,
            params={"access_token": token},
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
    text = text.replace("\u00e9", "e")
    text = re.sub(r'%[A-Z|0-9]{2}', '', text)
    text = re.sub(r'[0-9]', '', text)
    text = re.sub(r'[+]+', '+', text)
    return text


def parse_response(text):
    global key_id
    #Check if is a url
    is_url = 'https://l.facebook.com' in text
    if is_url:
        #Now parse url,
        text = unquote(text)
        lat_lon = text.split("where1=")[1].split("&")[0].replace("%2C+", "%")
        lat = lat_lon.split("%")[0]
        lon = lat_lon.split("%")[-1]
    else:
        try:
            lat, lon = ast.literal_eval(text)
        except:
            return {"edo": "", "mun": ""}
        try:
            lat = float(lat)
            lon = float(lon)
            url = GOOGLE_LATLON % (lat, lon, google_tokens[key_id])
            request = requests.get(url)
            if request.status_code >= 400:
                key_id = key_id + 1 if key_id+1 < len(google_tokens) else 0
                url = GOOGLE_LATLON % (lat, lon, google_tokens[key_id])
                request = requests.get(url)
            page = request.json()["results"]
        except ValueError:
            lat_lon = aux_parse_url_to_text(lat_lon)
            url = GOOGLE_ADDRESS + lat_lon + "&key=" +  google_tokens[key_id]
            request = requests.get(url)
            if request.status_code >= 400:
                key_id = key_id + 1 if key_id+1 < len(google_tokens) else 0
                url = GOOGLE_ADDRESS + lat_lon + "&key=" +  google_tokens[key_id]
                request = requests.get(url)
            page = request.json()["results"]
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


################################################################################
#                           BANSEFI FUNCTIONS                                  #
################################################################################
def get_distance(point_a, point_b):
    lon1 = radians(point_a[LON_IDX])
    lon2 = radians(point_b[LON_IDX])
    lat1 = radians(point_a[LAT_IDX])
    lat2 = radians(point_b[LAT_IDX])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R_EARTH * c

def get_nearest_bansefi_bank(point_a):
    global key_id
    base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&radius=20000&keyword=bansefi&type=bank&key=%s'
    full_url = base_url%(str(point_a[LAT_IDX]),str(point_a[LON_IDX]),google_tokens[key_id])
    r = requests.get(full_url)
    if r.status_code >= 400:
        key_id = key_id + 1 if key_id+1 < len(google_tokens) else 0
        full_url = base_url%(str(point_a[LAT_IDX]),str(point_a[LON_IDX]),google_tokens[key_id])
        r = requests.get(full_url)
    result_json = r.json()
    min_distance = sys.maxsize
    for item in result_json['results']:
        point_b =  item['geometry']['location']
        distance_item = get_distance(point_a, point_b)
        if min_distance > distance_item:
            min_distance = distance_item
            min_point = point_b
            min_place_id = item[PLACE_ID]

    if min_distance != sys.maxsize:
        return {LAT_IDX: min_point[LAT_IDX], LON_IDX: min_point[LON_IDX], PLACE_ID: min_place_id, 'distance': min_distance}

def get_bansefi_reference(text):
    global key_id
    is_url = 'https://l.facebook.com' in text
    if is_url:
        #Now parse url,
        text = unquote(text)
        lat_lon = text.split("where1=")[1].split("&")[0].replace("%2C+", "%")
        lat = lat_lon.split("%")[0]
        lon = lat_lon.split("%")[-1]
    else:
        try:
            lat, lon = ast.literal_eval(text)
        except:
            return {"reference": ""}
    dic = get_nearest_bansefi_bank({LAT_IDX: lat, LON_IDX:lon})
    url = 'https://maps.googleapis.com/maps/api/place/details/json?languaje=es&place_id=%s&key=%s'

    full_url = url%(dic[PLACE_ID], google_tokens[key_id])
    r = requests.get(full_url)
    if r.status_code >= 400:
        key_id = key_id + 1 if key_id+1 < len(google_tokens) else 0
        full_url = url%(dic[PLACE_ID], google_tokens[key_id])
        r = requests.get(full_url)
    result_json = r.json()

    day = datetime.now().weekday()
    if len(result_json["result"]["opening_hours"]["weekday_text"]) > day:
        h_string = str(result_json["result"]["opening_hours"]["weekday_text"][day])
        h_string = ':'.join(h_string.split(':')[1:]).replace("\u2013","-")
    else:
        h_string = "El dia de hoy no se encuentra abierto" 
    return {"direccion": aux_parse_url_to_text(result_json['result']['formatted_address']),
            "telefono" : result_json['result']['formatted_phone_number'],
            "horario"  : h_string
            }

################################################################################
#                           FACEBOOK FUNCTIONS                                 #
################################################################################

def build_template( image, title, subtitle, url =None, postback = None):
    buttons = []
    if url:
        buttons.append(Template.ButtonWeb(url["text"], url["content"]))
    if postback:
        buttons.append(Template.ButtonPostBack(postback["text"],
                                postback["content"]))
    return Template.GenericElement(
        title,
        subtitle=subtitle,
        image_url=image,
        item_url=url,
        buttons=buttons
        )


def send_bank_info(image, title, subtitle, url = None,recipient_id = "1491985787521789"):
    page = Page(FACEBOOK_TOKEN_3)
    news = []
    template = build_template(image= image,
                              title= title,
                              subtitle= subtitle,
                              url = url)
    news.append(template)
    page.send(recipient_id, Template.Generic(news))


def send_active_resources(recipient_id = "1491985787521789"):
    page = Page(FACEBOOK_TOKEN_3)
    news = []
    template = build_template(image= "https://rapidpro.datos.gob.mx/media/FECHA_DE_PAGO.png",
                              title= "Proxima fecha de pago",
                              subtitle= "Te recordaremos cuando sea tu proxima fecha de pago",
                              postback = {"text": "Fecha de pago", "content": "PAYDAY"}
                              )
    news.append(template)
    template = build_template(image= "https://rapidpro.datos.gob.mx/media/AHORRO.png",
                              title= "Ahorra",
                              subtitle= "Recibe informacion que te ayudara a ahorrar",
                              postback = {"text": "Ahorra", "content": "SAVING"}
                              )
    news.append(template)
    template = build_template(image= "https://rapidpro.datos.gob.mx/media/BANSEFI.png",
                              title= "Bansefi mas cercano?",
                              subtitle= "Consulta tu banco mas cercano",
                              postback = {"text": "Conoce", "content": "BANSEFI"}
                              )
    news.append(template)
    page.send(recipient_id, Template.List(elements=news,  buttons=[
                    {"title": "No, gracias", "type": "postback", "payload": "ss"}]))
