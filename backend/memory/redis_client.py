import os
import json
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )

    def set_state(self, task_id: str, state: dict, ex: int = 3600):
        """Stores execution state with an expiry (default 1 hour)"""
        self.client.set(f"task:{task_id}:state", json.dumps(state), ex=ex)

    def get_state(self, task_id: str) -> dict:
        """Retrieves current task execution state"""
        data = self.client.get(f"task:{task_id}:state")
        if data:
            return json.loads(data)
        return {}

    def delete_state(self, task_id: str):
        self.client.delete(f"task:{task_id}:state")

    def publish_update(self, channel: str, message: dict):
        self.client.publish(channel, json.dumps(message))
