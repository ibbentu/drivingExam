from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def index():
    return "Hello Flask + Granian + Docker!"


@app.get("/health")
def health():
    return jsonify({
        "status": "ok",
        "server": "granian",
        "framework": "flask"
    })


@app.get("/api/quiz")
def quiz_sample():
    return jsonify({
        "id": 1,
        "question": "Granian은 Flask를 어떤 인터페이스로 실행하나요?",
        "choices": ["ASGI", "WSGI", "RSGI", "CGI"],
        "answer": "WSGI"
    })