from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# MongoDB configuration
client = MongoClient(os.getenv('MONGO_URI'))
db = client.github_actions
actions_collection = db.repository_actions

@app.route('/github-webhook', methods=['POST'])
def github_webhook():
    if request.method == 'POST':
        payload = request.json
        event_type = request.headers.get('X-GitHub-Event')
        
        if event_type == 'push':
            event_data = {
                "request_id": payload['after'],
                "author": payload['pusher']['name'],
                "action": "PUSH",
                "from_branch": None,
                "to_branch": payload['ref'].split('/')[-1],
                "timestamp": datetime.utcnow().isoformat() + 'Z'
            }
        
        elif event_type == 'pull_request':
            pr_action = payload['action']
            if pr_action == 'opened':
                event_data = {
                    "request_id": str(payload['pull_request']['number']),
                    "author": payload['pull_request']['user']['login'],
                    "action": "PULL_REQUEST",
                    "from_branch": payload['pull_request']['head']['ref'],
                    "to_branch": payload['pull_request']['base']['ref'],
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            elif pr_action == 'closed' and payload['pull_request']['merged']:
                event_data = {
                    "request_id": str(payload['pull_request']['number']),
                    "author": payload['pull_request']['merged_by']['login'],
                    "action": "MERGE",
                    "from_branch": payload['pull_request']['head']['ref'],
                    "to_branch": payload['pull_request']['base']['ref'],
                    "timestamp": datetime.utcnow().isoformat() + 'Z'
                }
            else:
                return jsonify({"status": "ignored"}), 200
        
        else:
            return jsonify({"status": "ignored"}), 200
        
        actions_collection.insert_one(event_data)
        return jsonify({"status": "success"}), 200

    return jsonify({"status": "error"}), 400

@app.route('/api/actions', methods=['GET'])
def get_actions():
    actions = list(actions_collection.find().sort("timestamp", -1).limit(10))
    # Convert ObjectId to string for JSON serialization
    for action in actions:
        action['_id'] = str(action['_id'])
    return jsonify(actions)

if __name__ == '__main__':
    app.run(debug=True)