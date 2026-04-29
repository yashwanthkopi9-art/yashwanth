import os
from flask import Flask, request, render_template_string
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

app = Flask(__name__)

ACCOUNT_SID = os.getenv("TWILIO_TEST_ACCOUNT_SID", "ACca18f645c981f9d443c6498dd8d63726")
AUTH_TOKEN = os.getenv("TWILIO_TEST_AUTH_TOKEN", "fe22a8e555b59cfb2202849fd17a2338")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Twilio API Test</title>
</head>
<body>
    <h2>Send Test SMS</h2>
    <form method="POST" action="/send">
        To: <input name="to" value="+15005550006"><br>
        Message: <input name="body" value="Hello from test"><br>
        <button type="submit">Send</button>
    </form>

    <h2>Get Messages</h2>
    <form method="GET" action="/messages">
        <button type="submit">Fetch Logs</button>
    </form>

    <h2>Redact Message</h2>
    <form method="POST" action="/redact">
        Message SID: <input name="sid"><br>
        <button type="submit">Redact</button>
    </form>

    <hr>
    <div>{{ result|safe }}</div>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML, result="")

@app.route("/send", methods=["POST"])
def send_sms():
    try:
        message = client.messages.create(
            body=request.form.get("body"),
            from_="+15005550006",
            to=request.form.get("to")
        )
        return render_template_string(HTML, result=f"Sent! SID: {message.sid}")
    except TwilioRestException as e:
        return render_template_string(HTML, result=f"Error: {e.msg}")

@app.route("/messages")
def get_messages():
    try:
        messages = client.messages.list(limit=5)
        result = "<br>".join(
            f"SID: {m.sid} | Status: {m.status} | Body: {m.body}" for m in messages
        )
        return render_template_string(HTML, result=result)
    except TwilioRestException as e:
        return render_template_string(HTML, result=f"Error: {e.msg}")

@app.route("/redact", methods=["POST"])
def redact():
    try:
        sid = request.form.get("sid")
        message = client.messages(sid).update(body="")
        return render_template_string(HTML, result=f"Redacted SID: {message.sid}")
    except TwilioRestException as e:
        return render_template_string(HTML, result=f"Error: {e.msg}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
