import os

REDIS_URL = os.getenv('redis_endpoint','redis://192.168.99.100')
QUEUES = ['download-queue','download-failed']

print("Redis info: from worker settings: " + REDIS_URL)
