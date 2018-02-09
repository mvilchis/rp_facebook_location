import os

################ Facebook environment variables ################
FACEBOOK_TOKEN = os.getenv("FACEBOOK_TOKEN","")
FACEBOOK_URL= "https://graph.facebook.com/v2.6/me/messages"
