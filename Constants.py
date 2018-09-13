import os

################ Facebook environment variables ################
FACEBOOK_TOKEN_1 = os.getenv("FACEBOOK_TOKEN_1", "") # Misalud
FACEBOOK_TOKEN_2 = os.getenv("FACEBOOK_TOKEN_2", "") # Secretaria de salu
FACEBOOK_TOKEN_3 = os.getenv("FACEBOOK_TOKEN_3", "") # Prospera digital
FACEBOOK_URL = "https://graph.facebook.com/v2.6/me/messages"

########################## Google urls ########################
GOOGLE_LATLON = "https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=false&&key=%s"
GOOGLE_ADDRESS  = "https://maps.googleapis.com/maps/api/geocode/json?address="
