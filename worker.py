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
import json
import uuid

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

elasticsearch_host = os.getenv('elasticsearch_host','http://docker:9200')

elasticsearch_endpoint=elasticsearch_host+'/bank/transactions/'
esheaders = {'Accept':'application/json','Content-Type':'application/json'}

auth = os.getenv('auth','INVALID_TOKEN_DEFAULT\n')
auth = auth.replace('\n', '')

headers = {'Host':'www.bnz.co.nz',
           'Connection':'keep-alive',
           'Pragma':'no-cache',
           'Cache-Control':'no-cache',
           'Accept':'application/json, text/javascript, */*; q=0.01','X-API-Client-ID':'YouMoney',
           'X-Requested-With':'XMLHttpRequest',
           'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/56.0.2924.87 Safari/537.36',
            'Referer':'https://www.bnz.co.nz/client/',
            'Accept-Encoding':'gzip, deflate, sdch, br',
            'Accept-Language':'en-US,en;q=0.8,es;q=0.6,it-IT;q=0.4,it;q=0.2',
            'Cookie':auth}


redis_host = os.getenv('redis_endpoint','docker')
q = Queue('process-queue',connection=Redis(host=redis_host))

mongodb_host = os.getenv('mongodb_endpoint','docker:27017')
client = MongoClient(host=[mongodb_host])
db = client.test


def get_transactions(id):
    logging.debug('Getting data from period: ' + str(id))
    transaction = db.bank.find_one(id)
    start_period=transaction.get('Period')
    end_period=str((datetime.strptime(transaction.get('Period'), '%Y-%m-%d') + timedelta(days=6)).date()) #FIXME: Weekly
    endpoint = transaction.get('Account').get('ENDPOINT') + '/transactions?startDate=' + start_period + '&endDate=' + end_period
    r = requests.get(endpoint,headers=headers, verify=True) #FIXME
    if r.status_code == 200:
        logging.debug('OK! Marking as Downloaded and adding transactions data to the database')
        transaction['Transactions']= r.json()
        db.bank.update({'_id': id}, {"$set": transaction}, upsert=False)
        logging.info('Sending a new message queue to process the files')
        job = q.enqueue(import_data_in_elastic_search, id)
    else:
        logging.error('Could not get data')
    logging.debug('Complete')


def get_time(date, time):
    # transaction.get('date')+"T"+transaction.get('time')+"+13:00"
    offset="+12:00"
    iso_8601=date+"T"+time+offset
    return iso_8601


def import_data_in_elastic_search(id):

    logging.debug('Importing...' + id)
    transaction = db.bank.find_one(id)
    data = transaction.get('Transactions')
    transactions_list = data.get('transactions')
    if len(transactions_list) > 0:
        for transaction in transactions_list:
            try:
                new_transaction = {"timestamp": get_time(transaction.get('date'), transaction.get('time')),
                                   'amount': transaction.get('amount'),
                                   'description': transaction.get('description'),
                                   "fromStatementDetails": transaction.get('fromStatementDetails'),
                                   "otherPartyName": transaction.get('otherPartyName'),
                                   "transactionTypeCode": transaction.get('transactionTypeCode'),
                                   "transactionTypeDescription": transaction.get('transactionTypeDescription')}
            except KeyError:
                pass
            send_to_elastic_search(new_transaction, uuid.uuid1())
        logging.debug('Importing Complete. ENJOY!')
    else:
        logging.info('The requested period have not transactions')


def send_to_elastic_search(document,index):
    logging.info('Importing data into elastic search')
    request = requests.put(elasticsearch_endpoint+str(index), headers=esheaders, json=document)
    print(request.status_code)
