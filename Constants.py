import os

################ Facebook environment variables ################
FACEBOOK_TOKEN = os.getenv("FACEBOOK_TOKEN", "")
FACEBOOK_URL = "https://graph.facebook.com/v2.6/me/messages"

########################## Google urls ########################
GOOGLE_LATLON = "https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=false&&key=%s"
GOOGLE_ADDRESS  = "https://maps.googleapis.com/maps/api/geocode/json?address="
