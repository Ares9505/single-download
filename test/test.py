import pymongo
import urllib.parse
import random
       

user = urllib.parse.quote_plus('lyra')
print(user)
password = urllib.parse.quote_plus('FE7PNKlm%q^I') 
print(password)
print(f'mongodb://{user}:{password}@127.0.0.1:27017')
      