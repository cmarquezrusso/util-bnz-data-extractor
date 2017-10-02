import os

REDIS_URL = os.getenv('redis_endpoint','redis://docker')
QUEUES = ['download-queue','download-failed']

print("Redis info: from worker settings: " + REDIS_URL)
