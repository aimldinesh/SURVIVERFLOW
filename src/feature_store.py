import redis
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class RedisFeatureStore:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", None)
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))

        if redis_url:
            # Cloud (e.g. Upstash on Render)
            self.client = redis.StrictRedis.from_url(redis_url, decode_responses=True)
        else:
            # Local Docker Redis
            self.client = redis.StrictRedis(
                host=redis_host, port=redis_port, db=0, decode_responses=True
            )

    def store_features(self, entity_id, features):
        key = f"entity:{entity_id}:features"
        self.client.set(key, json.dumps(features))

    def get_features(self, entity_id):
        key = f"entity:{entity_id}:features"
        features = self.client.get(key)
        if features:
            return json.loads(features)
        return None

    def store_batch_features(self, batch_data):
        for entity_id, features in batch_data.items():
            self.store_features(entity_id, features)

    def get_batch_features(self, entity_ids):
        return {eid: self.get_features(eid) for eid in entity_ids}

    def get_all_entity_ids(self):
        keys = self.client.keys("entity:*:features")
        return [key.split(":")[1] for key in keys]
