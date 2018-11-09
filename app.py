from flask import Flask, jsonify
from threading import Thread

from utils import *
from webargs import fields
from webargs.flaskparser import use_kwargs
app = Flask(__name__)

#############################################################
#                     Restrictions                          #
#############################################################
location_args = {
    'urn': fields.String(required=True),
    'text': fields.String(required=True)
}
parse_args = {
    'location': fields.String(required=True)
}

bansefi_args = {
    'location': fields.String(required=True)
}
campaign_args = {
    'urn': fields.String(required=True),
}
def create_thread_location(urn, text):
    thread = Thread(target = send_location, args=(urn,text))
    thread.start()
    return

def create_thread_campaign(urn):
    thread = Thread(target = send_active_resources, args=(urn,))
    thread.start()
    return

#############################################################
#                      Endpoints                            #
#############################################################
@app.route("/", methods=['POST', 'GET'])
@use_kwargs(location_args)
def view_send_location(urn, text):
    create_thread(urn,text)
    return jsonify({"ok": "ok"})

@app.route("/parse", methods=['GET'])
@use_kwargs(parse_args)
def view_parse_location(location):
    return jsonify(parse_response(location))

@app.route("/bansefi", methods=['POST', 'GET'])
@use_kwargs(bansefi_args)
def view_bansefi_reference(location):
    nearest_bansefi = get_bansefi_reference(location)
    return jsonify(nearest_bansefi)


@app.route("/campaign_prospera", methods=['POST', 'GET'])
@use_kwargs(campaign_args)
def view_campaign_prospera(urn):
    create_thread_campaign(urn)
    return jsonify({"ok": "ok"})

@app.route("/parse_fb_loc", methods=['POST', 'GET'])
@use_kwargs(bansefi_args)
def view_parse_fb_loc(location):
    lat_lon = get_lat_lon(location)
    return jsonify(lat_lon)


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(
        debug=True, host="0.0.0.0", port=int(os.getenv('WEBHOOK_PORT', 5000)))
