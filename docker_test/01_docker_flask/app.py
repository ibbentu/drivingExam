from flask import Flask

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello Flask in Docker!"

@app.route("/health")
def health():
    return {"status": "ok"}