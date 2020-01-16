from flask import Flask
from flask import request
from flask import jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def parseIntent():
	intent = request.args.get('intent')
	print(intent)

	if "yeet" not in intent:
		return jsonify({'status': 'bad intent'}), 403
	return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='localhost', port=8081)
