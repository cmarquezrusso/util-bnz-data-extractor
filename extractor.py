import requests
import time
import json
import os
import errno
from datetime import datetime, timedelta
import threading
import logging


logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-10s) %(message)s',
                    )

BASE_URL= "https://www.bnz.co.nz"
ENDPOINT = BASE_URL + "/ib/api/accounts/"

auth = os.getenv('auth','12345').replace(('\n', ''))
import pprint; pprint.pprint(auth);

startdate='2015-09-16'
enddate=time.strftime("%Y-%m-%d")
folder='data/'
workers=0

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
download_queue=[]


def download_worker():
    for pending_download in download_queue:
        r = requests.get(pending_download.get('ENDPOINT')+"/transactions?startDate="+pending_download.get('Start')+"&endDate="+pending_download.get('End'),
                         headers=headers, verify=True)
        if r.status_code == 200 :
            save_json_to_file(pending_download.get('file'), r.json())
        else:
            logging.error('Could not get data')


def save_json_to_file(file, data):
    logging.debug(file)
    if not os.path.exists(os.path.dirname(folder)):
        try:
            os.makedirs(os.path.dirname(folder))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(folder+file, 'w') as outfile:
        json.dump(data, outfile,sort_keys=True, indent=4)


def get_accounts():
    logging.info('Connecting to BNZ to get a list of Bank Accounts')
    logging.info('Connected')

    accounts=[]
    r = requests.get(ENDPOINT, headers=headers, verify=True, allow_redirects=False)
    if r.status_code != 200:
        logging.error("Response is not OK. Maybe your token has expired")
        exit(-1)
    accounts_info=r.json()
    for account in accounts_info['accountList']:
        account_data={"id":account['id'],"nickname":account['nickname'],"ENDPOINT": ENDPOINT + account['id']}
        accounts.append(account_data)
        logging.info('Downloading data from account: ' + account.get('nickname'))
    workers = len(accounts) #TODO: Multithreading for performance
    logging.info(str(workers) + " accounts received from BNZ.")
    logging.info(str(workers) + " workers will be used for downloading")
    return accounts


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)


def weeks(days):
    return days/7


def get_intervals():
    logging.debug('Building Date Intervals')
    weeks_diff = weeks(days_between(startdate, enddate))
    intervals = []
    init_date = datetime.strptime(startdate, "%Y-%m-%d")
    while (weeks_diff > 0):
        interval = dict()
        interval['Start'] = str(init_date.date())
        interval['End']= str(init_date.date() + timedelta(days=7))
        interval['WeekNumber'] = datetime.date(init_date).isocalendar()[1]
        interval['Year'] = init_date.year
        init_date = init_date + timedelta(days=8)
        intervals.append(interval)
        weeks_diff -= 1
    return intervals


def start():
    transactions = list()
    for account in get_accounts():
        for interval in get_intervals():
            transaction_info=dict()
            transaction_info['file'] = (account['nickname']+str(interval.get('Year'))+"-W-" + str(interval.get('WeekNumber')) + ".json")
            transaction_info['Start'] = interval.get('Start')
            transaction_info['End'] = interval.get('End')
            transaction_info['nickname']= account.get('nickname')
            transaction_info['ENDPOINT']= account.get('ENDPOINT')
            transactions.append(transaction_info)

    logging.debug('Looking for existing files')

    for transaction in transactions:
        import os.path
        full_path_file=str(folder)+"/"+str(transaction.get('file'))
        if(os.path.isfile(full_path_file)):
            logging.info('File' + full_path_file + ' already downloaded. Skipping...')
        else:
            logging.debug('File ' + full_path_file + ' not found. Adding it to the download queue.')
            download_queue.append(transaction)

    download_worker()


if __name__ == "__main__":
    start()
