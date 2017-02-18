# util-bnz-data-extractor
A simple python script to consume the BNZ API and export it to ElasticSearch

Please vote for an accesable API into https://community.bnz.co.nz/t/api-application-programming-interface/337

Disclaimer: Work in Progress

# Project requirements

- Python 2.7
- Virtualenv
- Pip

# Getting started
- Install project dependencies by typing 
  ```
  $ virtualenv . --python /usr/bin/python2.7 
  $ pip install -r requirements.txt
  ```
- Edit extractor.py and add your Cookie from the BNZ Website or BNZ app (Google Chrome Inspector will help you here)
- Run extractor.py, this will generate a data folder with your transactions
- Run adapter.py, this will upload your transactions into elastic search. 

# Credits 

[Cristian Russo](http://www.cristianmarquez.me)
