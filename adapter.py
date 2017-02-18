from os import walk
import os
import json
import errno
import time
import requests
import uuid

folder = "data/"
proccessed_folder="data/proccesed/"

url='http://docker:9200/bank/transactions/'
headers = {'Accept':'application/json','Content-Type':'application/json'}


def send_to_elastic_search(document,index):
    r = requests.put(url+str(index), headers=headers, data=json.dumps(document))
    print(r.status_code)


def process_files():
    for report in get_files():
        transactions = open_data(folder + report)
        for transaction in transactions:
            send_to_elastic_search(transaction,uuid.uuid1())
        save_json_to_file(proccessed_folder + "proccesed-"+report,transactions)


def save_json_to_file(file, data):
    if not os.path.exists(os.path.dirname(file)):
        try:
            os.makedirs(os.path.dirname(file))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(file, 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)


def open_data(file):
    transactions = []
    with open(file) as data_file:
        data = json.load(data_file)
        for transaction in data['transactions']:
            try:
                new_transaction = {"timestamp": get_time(transaction.get('date'), transaction.get('time')),
                                   'amount': transaction.get('amount'),
                                   'description': transaction.get('description'),
                                   "fromStatementDetails": transaction.get('fromStatementDetails'),
                                   "otherPartyName": transaction.get('otherPartyName'),
                                   "transactionTypeCode": transaction.get('transactionTypeCode'),
                                   "transactionTypeDescription": transaction.get('transactionTypeDescription')}
                transactions.append(new_transaction)
            except KeyError:
                pass
        return transactions


def get_time(date, time):
    # transaction.get('date')+"T"+transaction.get('time')+"+13:00"
    offset="+12:00"
    iso_8601=date+"T"+time+offset
    return iso_8601


def get_files():
    f = []
    for (dirpath, dirnames, filenames) in walk(folder):
        f.extend(filenames)
        break
    return f


if __name__ == "__main__":
    process_files()
