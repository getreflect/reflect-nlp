import logging

from serve_model import Model

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def healthCheck():
    logging.info("Health check ping received")
    return jsonify({'status': 'healthy'}), 200


@app.route('/', methods=['POST'])
def parseIntent():
    if request.is_json:
        intent = request.get_json()["intent"]

        # check if intent valid via NLP model
        if not m.pred(str(intent)):
            logging.warning("Got bad intent: " + intent)
            return jsonify({'status': 'bad intent'}), 403

        logging.info("OK intent: " + intent)
        return jsonify({'status': 'ok'}), 200

    logging.warning("Received non-JSON response.")
    return jsonify({'status': 'bad json'}), 400

if __name__ == '__main__':
    logging.info("Starting server...")
    m = Model("acc81.08", threshold=0.5)
    app.run()
