import os

REDIS_URL = os.getenv('redis_endpoint','redis://docker:6379')
QUEUES = ['process-queue', 'process-failed']

print("Redis info: from worker settings: " + REDIS_URL)
