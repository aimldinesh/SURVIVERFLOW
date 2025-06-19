import redis
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file (in dev/local)
load_dotenv()


class RedisFeatureStore:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))

        try:
            if redis_url:
                # If URL starts with rediss:// use TLS (for Upstash or Render secret)
                self.client = redis.StrictRedis.from_url(
                    redis_url, decode_responses=True
                )
                print("[Redis] Connected via REDIS_URL (TLS if rediss://)")
            else:
                # Local Redis (usually no TLS)
                self.client = redis.StrictRedis(
                    host=redis_host,
                    port=redis_port,
                    db=0,
                    decode_responses=True,
                    ssl=False,
                )
                print("[Redis] Connected via host/port")

            # Test connection
            self.client.ping()
            print("[Redis] Connection successful")

        except redis.ConnectionError as e:
            raise ConnectionError(f"[Redis] Connection failed: {e}")

    def store_features(self, entity_id, features):
        key = f"entity:{entity_id}:features"
        self.client.set(key, json.dumps(features))

    def get_features(self, entity_id):
        key = f"entity:{entity_id}:features"
        features = self.client.get(key)
        return json.loads(features) if features else None

    def store_batch_features(self, batch_data):
        for entity_id, features in batch_data.items():
            self.store_features(entity_id, features)

    def get_batch_features(self, entity_ids):
        return {eid: self.get_features(eid) for eid in entity_ids}

    def get_all_entity_ids(self):
        keys = self.client.keys("entity:*:features")
        return [key.split(":")[1] for key in keys]
