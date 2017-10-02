# util-bnz-data-extractor
A simple python script to consume the BNZ API and export it to ElasticSearch

Please vote for an API into https://community.bnz.co.nz/t/api-application-programming-interface/337

Disclaimer: Work in Progress

# Project requirements

- Python 2.7
- Virtualenv
- Pip
- Docker

# Getting started

- Install project dependencies by typing 
  ```
  $ virtualenv . --python /usr/bin/python2.7 
  $ pip install -r requirements.txt
  ```

docker-machine ssh

sudo sysctl -w vm.max_map_count=262144

docker-compose up elasticsearch kibana database message-queue workers-dashboard 

nmap docker -p 27017,9181,5601,6379,9200,9300

rq worker -c processor-worker-settings

env auth='' rq worker -c download-worker-settings

env auth='' start_date='2014-06-01' freq='w' python bnz-extractor.py 


# Credits 

[Cristian Russo](http://www.cristianmarquez.me)


