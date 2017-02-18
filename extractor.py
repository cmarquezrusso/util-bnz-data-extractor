import requests
import time
import json
import os
import errno

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
            'Cookie':'ADD-YOUR-KEY-HERE'}

base_url= "https://www.bnz.co.nz"
from_date="2015-01-01"
end_date=time.strftime("%Y-%m-%d") # Today
endpoint = base_url + "/ib/api/accounts/"
folder = "data/"


def main():
    for account in get_accounts():
        r = requests.get(account['endpoint']+"/transactions?startDate="+from_date+"&endDate="+end_date,
                         headers=headers, verify=True)
        if r.status_code == 200 :
            save_json_to_file(account['nickname']+".json", r.json())
        else:
            print('Could not get data')


def save_json_to_file(file, data):
    if not os.path.exists(os.path.dirname(folder)):
        try:
            os.makedirs(os.path.dirname(folder))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(folder+file, 'w') as outfile:
        json.dump(data, outfile,sort_keys=True, indent=4)


def get_accounts():
    accounts=[]
    r = requests.get(endpoint, headers=headers, verify=True)
    accounts_info=r.json()
    for account in accounts_info['accountList']:
        account_data={"id":account['id'],"nickname":account['nickname'],"endpoint": endpoint + account['id']}
        accounts.append(account_data)
    return accounts


if __name__ == "__main__":
    main()