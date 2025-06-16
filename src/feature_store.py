import redis
import json


class RedisFeatureStore:
    def __init__(self, host="localhost", port=6379, db=0):
        # Initialize Redis client connection
        self.client = redis.StrictRedis(
            host=host,
            port=port,
            db=db,
            decode_responses=True,  # Ensures responses are returned as strings (not bytes)
        )

    # Store features for a single entity (e.g., user/product)
    def store_features(self, entity_id, features):
        key = f"entity:{entity_id}:features"  # Key format in Redis
        self.client.set(
            key, json.dumps(features)
        )  # Store the features as a JSON string

    # Retrieve features for a single entity
    def get_features(self, entity_id):
        key = f"entity:{entity_id}:features"
        features = self.client.get(key)  # Fetch value from Redis
        if features:
            return json.loads(features)  # Convert JSON string back to dictionary
        return None

    # Store features for multiple entities in batch
    def store_batch_features(self, batch_data):
        for entity_id, features in batch_data.items():
            self.store_features(entity_id, features)  # Reuse single store method

    # Retrieve features for multiple entities
    def get_batch_features(self, entity_ids):
        batch_features = {}
        for entity_id in entity_ids:
            batch_features[entity_id] = self.get_features(
                entity_id
            )  # Fetch each entity's features
        return batch_features

    # Get all entity IDs currently stored in Redis
    def get_all_entity_ids(self):
        keys = self.client.keys(
            "entity:*:features"
        )  # Match all keys following the entity pattern

        # Extract the entity_id from each key (format: entity:<id>:features)
        entity_ids = [key.split(":")[1] for key in keys]
        return entity_ids
