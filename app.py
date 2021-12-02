from flask import Flask, render_template, request, jsonify
#from werkzeug.wrappers import response
#from flask_cors import CORS
from all_chat import get_response
from conversation import read_input

app = Flask(__name__)
#CORS(app)

@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    #TODO: check the text validity
    response = get_response(text,request)
    message = {"answer": response}
    return jsonify(message)

if __name__=="__main__":
    app.run(port=5000, debug=True)        