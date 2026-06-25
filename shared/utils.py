import uuid
import json
from datetime import datetime
from typing import Dict, Any
import redis
import os

def generate_id():
    return str(uuid.uuid4())

def get_redis_client():
    return redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        decode_responses=True
    )

def publish_event(channel: str, event: Dict[str, Any]):
    """Publish event to Redis channel for inter-service communication"""
    redis_client = get_redis_client()
    redis_client.publish(channel, json.dumps(event))
