# util-bnz-data-extractor
A ~~simple~~ python script to consume the BNZ API and export it to ElasticSearch

Please vote for an API into https://community.bnz.co.nz/t/api-application-programming-interface/337

Disclaimer: Work in Progress

# Project requirements

- Python 2.7
- Virtualenv
- Pip
- Docker
- Docker-machine
- Docker-compose

# Architecture

Use stackedit.io to see this.

```sequence
BNZ Extractor->BNZ API: Get accounts
BNZ API->BNZ Extractor: List of accounts
BNZ Extractor->Download Worker: Notify
BNZ Extractor->MongoDB: Initial Structure
Download Worker->BNZ API: Get transactions
BNZ API->Download Worker: transaction
Download Worker->MongoDB: Insert transactions
Download Worker->Process Worker: Notify
Process Worker->Elastic Search: Import transaction
Kibana->Elastic Search: Discovery
```


# Getting started

- Install project dependencies by typing 
  ```
  $ virtualenv . --python /usr/bin/python2.7 
  $ pip install -r requirements.txt
  ```

```
docker-machine ssh

 sudo sysctl -w vm.max_map_count=262144
 exit
 
```

```
docker-compose up elasticsearch kibana database message-queue workers-dashboard 
```

```
nmap 192.168.99.100 -p 27017,9181,5601,6379,9200,9300 # Just to test that everything is on place
```

```
rq worker -c processor-worker-settings # Turn on the worker to import into ES
```
```
env auth='' rq worker -c download-worker-settings # Start the worker to download from BNZ
```
```
env auth='' start_date='2014-06-01' freq='w' python bnz-extractor.py # Start the app that creates the initial structure
```

# Credits 

[Cristian Russo](http://www.cristianmarquez.me)


