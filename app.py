import asyncio
from dotenv import load_dotenv
import os
import json
from hume import HumeStreamClient
from hume.models.config import LanguageConfig, ProsodyConfig
from pymongo import MongoClient
from db_utils import connect_to_mongo, deduplicate_records, find_and_update_highest_emotion, find_and_update_top5_emotions
from uuid import uuid4
from datetime import datetime
from flask import Flask, render_template, jsonify, request


app = Flask(__name__)
load_dotenv()

api_key = os.environ.get("api_key")
mongo_link = os.environ.get("mongo_link")
if not api_key or not mongo_link:
    raise EnvironmentError("Failed to get environment variables")


@app.route('/submit_email', methods=['POST'])
def submit_email():
    data = request.json
    email = data.get('email')
    mongo_client_users = MongoClient(mongo_link)
    db_users = mongo_client_users['Users']
    collection_users = db_users['users']

    # Connect to emotionDB database
    mongo_client_emotion = MongoClient(mongo_link)
    db_emotion = mongo_client_emotion['emotionDB']
    collection_emotion = db_emotion['emotionData']
    if not email:
        return jsonify({'success': False, 'message': 'Email is required'}), 400
    existing_record = collection_users.find_one({"email": email})

    if existing_record:
        return jsonify({'success': False, 'message': 'Email already exists'}), 409

    # Save email to Users database
    collection_users.insert_one({"email": email})

    return jsonify({'success': True, 'message': 'Email saved successfully'}), 200


@app.route("/")
def index():
    return render_template("/index.html")


@app.route("/api/update_highest_emotion", methods=["POST"])
def update_highest_emotion():
    try:
        find_and_update_highest_emotion(collection_emotion)
        return jsonify({"success": True}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False}), 500


if __name__ == "__main__":
    # Connect to Users database

    app.run(host='0.0.0.0', port=8000)
