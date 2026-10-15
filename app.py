from flask import Flask
app = Flask(__name__)


@app.route("/")
def home():
  return "My first Flask application is running!"

app.run (debug=True)
