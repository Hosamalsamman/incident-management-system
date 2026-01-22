from flask import jsonify

from routes import create_app

app = create_app()

@app.route('/')
def home():  # put application's code here
    # print("test")
    return jsonify({"response": "بسم الله "})


if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000, debug=True)
