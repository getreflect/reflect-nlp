import logging

from serve_model import Model

import flask
from flask import jsonify
from flask import request

app = flask.Flask(__name__)


@app.route('/', methods=['GET'])
def healthCheck():
    logging.info("Health check ping received")
    return jsonify({'status': 'healthy'}), 200


@app.route('/api', methods=['POST'])
def parseIntent():
    data = flask.request.form  # is a dictionary
    intent = data['intent']

    # check if intent valid via NLP model
    if not m.pred(intent):
        logging.warning("Got bad intent: " + intent)
        return jsonify({'status': 'bad intent'}), 403

    logging.info("OK intent: " + intent)
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    logging.info("Starting server...")
    m = Model("acc81.08", threshold=0.5)
    app.run(host="0.0.0.0", port=5000)
