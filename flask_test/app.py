from flask import Flask, render_template, request, abort

app = Flask(__name__)

# 아주 작은 테스트라도 호스트를 제한하는 편이 안전합니다.
ALLOWED_HOSTS = {
    }

@app.before_request
def limit_host_header():
    if request.host not in ALLOWED_HOSTS:
        abort(400)

@app.after_request
def add_security_headers(response):
    # HTTPS 응답에 HSTS 부여
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

@app.route("/")
def index():
    return render_template("index.html")