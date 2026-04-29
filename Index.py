from flask import Flask, request, render_template_string
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

app = Flask(__name__)

ACCOUNT_SID = "ACca18f645c981f9d443c6498dd8d63726"
AUTH_TOKEN = "fe22a8e555b59cfb2202849fd17a2338"

client = Client(ACCOUNT_SID, AUTH_TOKEN)

HTML = """
<!DOCTYPE html>
<html>
<head><title>Twilio App</title></head>
<body>
<h2>Send SMS</h2>
<form method="POST" action="/send">
To: <input name="to" value="+15005550006"><br>
Message: <input name="body" value="Hello"><br>
<button type="submit">Send</button>
</form>

<h2>Messages</h2>
<form method="GET" action="/messages">
<button type="submit">Fetch</button>
</form>

<h2>Redact</h2>
<form method="POST" action="/redact">
SID: <input name="sid"><br>
<button type="submit">Redact</button>
</form>

<hr>
<div>{{ result|safe }}</div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML, result="")

@app.route("/send", methods=["POST"])
def send():
    try:
        msg = client.messages.create(
            body=request.form["body"],
            from_="+15005550006",
            to=request.form["to"]
        )
        return render_template_string(HTML, result=f"Sent: {msg.sid}")
    except TwilioRestException as e:
        return render_template_string(HTML, result=f"Error: {e.msg}")

@app.route("/messages", methods=["GET"])
def messages():
    try:
        msgs = client.messages.list(limit=5)
        result = "<br>".join(
            f"{m.sid} | {m.status} | {m.body}" for m in msgs
        )
        return render_template_string(HTML, result=result)
    except TwilioRestException as e:
        return render_template_string(HTML, result=f"Error: {e.msg}")

@app.route("/redact", methods=["POST"])
def redact():
    try:
        sid = request.form["sid"]
        msg = client.messages(sid).update(body="")
        return render_template_string(HTML, result=f"Redacted: {msg.sid}")
    except TwilioRestException as e:
        return render_template_string(HTML, result=f"Error: {e.msg}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
