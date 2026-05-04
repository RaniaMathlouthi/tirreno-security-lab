from flask import Flask, request, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

TIRRENO_URL = "http://localhost:8585/sensor/"
TIRRENO_KEY = "0499ad421a29a6ba487de429fbe47bf7"
BLACKLIST_URL = "http://localhost:8585/api/v1/blacklist/search"

USERS = {
    "alice": {"password": "password123", "email": "alice@gmail.com"},
    "bob":   {"password": "securepass",  "email": "bob@gmail.com"},
    "hacker": {"password": "hack123",   "email": "hacker@evil.com"},
}

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Demo Login</title></head>
<body style="font-family:Arial; max-width:400px; margin:100px auto;">
    <h2>🔐 Demo Login</h2>
    {% if message %}<p style="color:{{ color }}">{{ message }}</p>{% endif %}
    <form method="POST">
        <input name="username" placeholder="Username" style="display:block;margin:10px 0;padding:8px;width:100%"><br>
        <input name="password" type="password" placeholder="Password" style="display:block;margin:10px 0;padding:8px;width:100%"><br>
        <button type="submit" style="padding:10px 20px">Login</button>
    </form>
</body>
</html>
"""

def is_blacklisted(username):
    try:
        r = requests.post(BLACKLIST_URL, 
            headers={"Content-Type": "application/json", "Api-Key": TIRRENO_KEY},
            json={"value": username})
        return r.json().get("blacklisted", False)
    except:
        return False

def send_to_tirreno(username, email, ip, event_type):
    requests.post(TIRRENO_URL, headers={
        "Content-Type": "application/x-www-form-urlencoded",
        "Api-Key": TIRRENO_KEY
    }, data={
        "userName": username,
        "ipAddress": ip,
        "url": "/login",
        "userAgent": "Mozilla/5.0",
        "eventTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.000"),
        "eventType": event_type,
        "emailAddress": email
    })

@app.route("/", methods=["GET", "POST"])
def login():
    message = ""
    color = "black"
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        ip = request.remote_addr
        user = USERS.get(username)

        if is_blacklisted(username):
            message = f"🚫 Access denied — {username} is blacklisted!"
            color = "red"
        elif user and user["password"] == password:
            send_to_tirreno(username, user["email"], ip, "account_login")
            message = f"✅ Welcome {username}!"
            color = "green"
        else:
            email = user["email"] if user else f"{username}@unknown.com"
            send_to_tirreno(username, email, ip, "account_login_fail")
            message = "❌ Invalid credentials"
            color = "red"

    return render_template_string(LOGIN_PAGE, message=message, color=color)

if __name__ == "__main__":
    app.run(port=5000, debug=True)