from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

@app.route('/', methods=['GET'])
def healthCheck():
	logging.info("Health check ping received")
	return jsonify({'status': 'healthy'}), 200

@app.route('/', methods=['POST'])
def parseIntent():
	if request.is_json:
		intent = request.get_json()["intent"]

		if "work" not in intent:
			logging.warning("Got bad intent: " + intent)
			return jsonify({'status': 'bad intent'}), 403

		logging.info("OK intent: " + intent)
		return jsonify({'status': 'ok'}), 200

	logging.warning("Received non-JSON response.")
	return jsonify({'status': 'bad json'}), 400

if __name__ == '__main__':
	logging.info("Starting server...")
	app.run()