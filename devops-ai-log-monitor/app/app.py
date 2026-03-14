from flask import Flask
import re

app = Flask(__name__)

@app.route("/")
def monitor_logs():
    errors = []

    with open("/var/log/app.log") as file:
        logs = file.readlines()

    for line in logs:
        if re.search("ERROR|CRITICAL", line):
            errors.append(line)

    return {"errors": errors}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)