import asyncio
from hume import HumeStreamClient
from hume.models.config import LanguageConfig
from pymongo import MongoClient
from db_utils import connect_to_mongo, deduplicate_records, find_and_update_highest_emotion, find_and_update_top5_emotions
from dotenv import load_dotenv
import os
import json
from datetime import datetime

load_dotenv()
api_key = os.environ.get("api_key")
mongo_link = os.environ.get("mongo_link")
samples = ["Mary had a little lamb,",
           "Its fleece was white as snow.",
           "Everywhere the child went,",
           "The little lamb was sure to go.",
           "you are stupid, lamb, she bitched",
           "In today's episode, I will show you some of my favourite CSS properties out there. These cool css tips and tricks will help you upgrade your website to the next level. This list contains some CSS tricks and properties that you may not know of.",
           "new Test to see if we can have a sun shine day"
           "Brady bunch like in our evil intent"
           ]


async def main_text():
    masterlist = []  # List to hold all records
    mongo_client_users = MongoClient(mongo_link)
    db_users = mongo_client_users['Users']
    collection_users = db_users['users']

    # Connect to emotionDB database
    mongo_client_emotion = MongoClient(mongo_link)
    db_emotion = mongo_client_emotion['emotionDB']
    collection_emotion = db_emotion['emotionData']
    try:
        client = HumeStreamClient(api_key)
        config = LanguageConfig()
        async with client.connect([config]) as socket:
            for sample in samples:
                existing_record = collection_emotion.find_one(
                    {"sample_text": sample})

                if existing_record:
                    print(f"Record already exists for sample: {sample}")
                    masterlist.append(existing_record)
                    continue

                result = await socket.send_text(sample)
                emotions = result.get("language", {}).get(
                    "predictions", [])[0].get("emotions", {})

                if emotions:
                    record = {
                        "sample_text": sample,
                        "analysis": {"emotions": emotions},
                        "metadata": {
                            "source": "some_source_info",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    }
                    insert_result = collection_emotion.insert_one(record)
                    masterlist.append(record)
            find_and_update_top5_emotions(collection_emotion)
            deduplicate_records(collection_emotion)
        return masterlist

    except Exception as e:
        print(f"Final stage error: {e}")

    with open('masterlist.json', 'w', encoding='utf-8') as f:
        json.dump(masterlist, f, indent=4)

if __name__ == "__main__":
    asyncio.run(main_text())
