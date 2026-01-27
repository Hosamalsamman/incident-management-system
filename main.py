from flask import jsonify
from routes import create_app
from extensions import socketio

app = create_app()

@app.route('/')
def home():  # put application's code here
    # print("test")
    return jsonify({"response": "بسم الله "})


if __name__ == '__main__':

    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

