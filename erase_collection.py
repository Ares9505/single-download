import pymongo


myclient = pymongo.MongoClient("mongodb://localhost:27017/") #conexion con el gestor de base de datos

db = myclient["mydatabase"]

mycollection= db["uri_state"]

mycollection.drop()