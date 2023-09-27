from pymongo import MongoClient
import os
import json
from dotenv import load_dotenv

load_dotenv()
#mongo_link = os.environ.get("mongo_link")


def connect_to_mongo(mongo_link):
    try:
        mongo_client = MongoClient(mongo_link)
        db = mongo_client['emotionDB']
        collection = db['emotionData']
        return collection
    except Exception as e:
        print(f"DB Initialization Error: {e}")
        exit()



def find_and_update_highest_emotion(collection):
    all_records = collection.find()

    for record in all_records:
        highest_score = -1
        highest_emotion = ""
        sample_text = record['sample_text']

        for emotion in record['analysis']['emotions']:
            if emotion['score'] > highest_score:
                highest_score = emotion['score']
                highest_emotion = emotion['name']

        print(
            f"For sample_text '{sample_text}', the highest score is {highest_score} for emotion {highest_emotion}")

        collection.update_one(
            {"_id": record['_id']},
            {"$set": {"highest_score": highest_score,
                      "highest_emotion": highest_emotion}}
        )


def find_and_update_top5_emotions(collection):
    all_records = collection.find()

    for record in all_records:
        sample_text = record['sample_text']
        emotions = record['analysis']['emotions']

        # Sort the emotions by score in descending order and take the top 5
        top5_emotions = sorted(
            emotions, key=lambda x: x['score'], reverse=True)[:5]

        print(
            f"For sample_text '{sample_text}', the top 5 emotions are {top5_emotions}")

        collection.update_one(
            {"_id": record['_id']},
            {"$set": {"top5_emotions": top5_emotions}}
        )


def deduplicate_records(collection):
    pipeline = [
        {"$group": {"_id": "$sample_text", "unique_ids": {
            "$addToSet": "$_id"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]

    duplicates = list(collection.aggregate(pipeline))

    for duplicate in duplicates:
        del duplicate['unique_ids'][0]
        collection.delete_many({"_id": {"$in": duplicate['unique_ids']}})


# Connect to MongoDB
mongo_link = "your_mongo_connection_string_here"
collection = connect_to_mongo(mongo_link)

# Run the functions
# find_and_update_highest_emotion(collection)
# find_and_update_highest_lowest_emotions(collection)
# deduplicate_records(collection)
