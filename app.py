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

def create_thread(urn, text):
    thread = Thread(target = send_location, args=(urn,text))
    thread.start()
    return
#############################################################
#                      Endpoints                            #
#############################################################
@app.route("/", methods=['POST', 'GET'])
@use_kwargs(location_args)
def view_send_news(urn, text):
    create_thread(urn,text)
    return jsonify({"ok": "ok"})

@app.route("/parse", methods=['GET'])
@use_kwargs(parse_args)
def view_parse_location(location):
    return jsonify(parse_response(location))


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(
        debug=True, host="0.0.0.0", port=int(os.getenv('WEBHOOK_PORT', 5000)))
