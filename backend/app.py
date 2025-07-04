from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_URI"))
db = client.githubEventsDB
events = db.events

def format_timestamp():
    return datetime.utcnow().strftime('%-d %B %Y - %-I:%M %p UTC')

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = request.headers.get("X-GitHub-Event")

    if event_type == "push":
        author = data["pusher"]["name"]
        branch = data["ref"].split("/")[-1]
        events.insert_one({
            "type": "push",
            "message": f'{author} pushed to "{branch}" on {format_timestamp()}'
        })

    elif event_type == "pull_request":
        action = data["action"]
        pr = data["pull_request"]
        author = pr["user"]["login"]
        from_branch = pr["head"]["ref"]
        to_branch = pr["base"]["ref"]
        merged = pr.get("merged", False)

        if action == "opened":
            events.insert_one({
                "type": "pull_request",
                "message": f'{author} submitted a pull request from "{from_branch}" to "{to_branch}" on {format_timestamp()}'
            })
        elif action == "closed" and merged:
            events.insert_one({
                "type": "merge",
                "message": f'{author} merged branch "{from_branch}" to "{to_branch}" on {format_timestamp()}'
            })

    return jsonify({"status": "received"}), 200

@app.route("/events", methods=["GET"])
def get_events():
    all_events = list(events.find().sort("_id", -1).limit(10))
    return jsonify([e["message"] for e in all_events])

if __name__ == "__main__":
    app.run(port=5000)
