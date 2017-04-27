#!/usr/bin/env python

import logging
import pprint
from pymongo import MongoClient
import os
import requests
from datetime import datetime
from datetime import timedelta
import pdb
import time
from rq import Queue
from redis import Redis


logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

redis_host = os.getenv('redis_endpoint','docker')
q = Queue('process-queue',connection=Redis(host=redis_host))

mongodb_host = os.getenv('mongodb_endpoint','docker:27017')
client = MongoClient(host=[mongodb_host])
db = client.test

mocked=True;


def get_transactions(id):
    logging.debug('Getting data from period: ' + str(id))
    transaction = db.bank.find_one(id)
    start_period=transaction.get('Period')
    end_period=str((datetime.strptime(transaction.get('Period'), '%Y-%m-%d') + timedelta(days=7)).date())
    endpoint = transaction.get('Account').get('ENDPOINT') + '/transactions?startDate=' + start_period + '&endDate=' + end_period
    if mocked:
        r = requests.get('https://raw.githubusercontent.com/laravel/laravel/master/package.json') #FIXME
        if r.status_code == 200:
            logging.debug('OK! Marking as Downloaded and adding transactions data to the database')
            transaction['Transactions']= r.json()
            db.bank.update({'_id': id}, {"$set": transaction}, upsert=False)
            logging.info('Sending a new message queue to process the files')
            job = q.enqueue(import_data_in_elastic_search, id)

        else:
            logging.error('Could not get data')
    logging.debug('Complete')


def import_data_in_elastic_search(id):
    logging.debug('Importing...' + id)
    time.sleep(1) #TODO: LOGIC
    logging.debug('Importing Complete. ENJOY!')