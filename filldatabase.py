import pymongo


myclient = pymongo.MongoClient("mongodb://localhost:27017/") #conexion con el gestor de base de datos

db = myclient["mydatabase"]

mycollection= db["customers"]

x=mycollection.insert_many([
  {"uri": "1BLfQ6dPXmuDrFmbdfW7Jl", "state": "PENDING", "path": "PENDING" , "priority": 0 },
  {"uri": "3YBZIN3rekqsKxbJc9FZko", "state": "PENDING", "path": "PENDING" , "priority": 0 },
  {"uri": "1OEoNpiyqBghuEUaT6Je6U", "state": "PENDING", "path": "PENDING" , "priority": 0 },
  {"uri": "6eDImMU0RbxxTWqlEzpcom", "state": "PENDING", "path": "PENDING" , "priority": 0 },
  {"uri": "6C62fl8x0vzwxPqay8twie", "state": "PENDING", "path": "PENDING" , "priority": 0 }
  ])


print(myclient.list_database_names())
print(db.list_collection_names())
for x in mycollection.find():
  print(x)

