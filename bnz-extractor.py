#!/usr/bin/env python

import requests
import os
from datetime import date, datetime, timedelta
import logging
from redis import Redis
import pandas as pd
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from rq import Queue
from worker import get_transactions # added import!


mongodb_host = os.getenv('mongodb_endpoint','192.168.99.100:27017')
redis_host = os.getenv('redis_endpoint','192.168.99.100')
client = MongoClient(host=[mongodb_host])
db = client.test
q = Queue('download-queue',connection=Redis(host=redis_host))
logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s')
BASE_URL= "https://www.bnz.co.nz"
ENDPOINT = BASE_URL + "/ib/api/accounts/"
auth = os.getenv('auth','INVALID_TOKEN_DEFAULT\n')
auth = auth.replace('\n', '')
verify=True

start_date_string=os.getenv('start_date','2014-09-16')
start_date = datetime.strptime(start_date_string,'%Y-%m-%d').date()
end_date = date.today()
freq=os.getenv('freq','W')
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


def get_accounts(): #TODO: Test 0 account, 1 account and 3 accounts. Tests invalid login.

    logging.info('Connecting to BNZ to get a list of Bank Accounts')
    logging.info('Connected')

    accounts=[]
    r = requests.get(ENDPOINT, headers=headers, verify=verify, allow_redirects=False)
    if r.status_code != 200:
        logging.error("Response is not OK. Maybe your token has expired")
    accounts_info=r.json()
    for account in accounts_info['accountList']:
        account_data={"id":account['id'],"nickname":account['nickname'],"ENDPOINT": ENDPOINT + account['id']}
        accounts.append(account_data)
        logging.info('Downloading data from account: ' + account.get('nickname'))
    logging.info(str(len(accounts)) + " accounts received from BNZ.")
    return accounts


def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)


def main():
    datelist = pd.date_range(start_date, end_date, freq=freq).tolist()
    for account in get_accounts():
        for date_int in datelist:
            period = {
                '_id' : account.get('nickname') + '-' + str(date_int.date()),
                'Period': str(date_int.date()), #FIXME: Datetime
                'Account': account
            }
            try:
                result = db.bank.insert_one(period)
                logging.info("Added new record in db " + str(result.inserted_id))
                logging.info('Sending event to the message queue. ID ' + str(result.inserted_id) + ' is a new record')
                job = q.enqueue(get_transactions, result.inserted_id)

            except DuplicateKeyError:
                logging.debug('Record already exists. Skipping....')
                pass


if __name__ == "__main__":
    main()