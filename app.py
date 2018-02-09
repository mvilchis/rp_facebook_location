from flask import Flask, jsonify

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


#############################################################
#                      Endpoints                            #
#############################################################
@app.route("/", methods=['POST', 'GET'])
@use_kwargs(location_args)
def view_send_news(urn, text):
    send_location(urn, text)
    return jsonify({"ok": "ok"})


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(
        debug=True, host="0.0.0.0", port=int(os.getenv('WEBHOOK_PORT', 5000)))
