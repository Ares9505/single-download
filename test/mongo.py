import pymongo


#para usar la data base de mongo debes ejecutar mongod y mongo.exe antes, estos ejecutables
#se encuentran en C:\Program Files\MongoDB\Server\4.0\bin
myclient = pymongo.MongoClient("mongodb://localhost:27017/") #conexion con el gestor de base de datos

db = myclient["mydatabase"] #creacion de una base de datos

mycollection= db["customers"] #creacion de una coleccion

x=mycollection.insert_one({
	"edad": 20,
	"Empresa": "azinox"
	})
#darse cuenta de q aqui se pasa un diccionario de python para llenar un documento(record)

print(myclient.list_database_names())
print(db.list_collection_names())

#Aqui se llena el documento, al momento de llenarse el documento es que se crea la collecion y la base de datos 
print(x.inserted_id)

lista =[
	{ "name": "Amy", "address": "Apple st 652"},
  { "name": "Hannah", "address": "Mountain 21"},
  { "name": "Michael", "address": "Valley 345"},
  { "name": "Sandy", "address": "Ocean blvd 2"},
  { "name": "Betty", "address": "Green Grass 1"},
  { "name": "Richard", "address": "Sky st 331"},
  { "name": "Susan", "address": "One way 98"},
  { "name": "Vicky", "address": "Yellow Garden 2"},
  { "name": "Ben", "address": "Park Lane 38"},
  { "name": "William", "address": "Central st 954"},
  { "name": "Chuck", "address": "Main Road 989"},
  { "name": "Viola", "address": "Sideway 1633"}
]
# y=mycollection.insert_many(lista)
# print(y.inserted_ids)
#si no se especifica el id mongodb insertara un id como identificador único
#por tanto es recomendable hacerlo uno mismo

mylist = [
  { "_id": 1, "name": "John", "address": "Highway 37"},
  { "_id": 2, "name": "Peter", "address": "Lowstreet 27"},
  { "_id": 3, "name": "Amy", "address": "Apple st 652"},
  { "_id": 4, "name": "Hannah", "address": "Mountain 21"},
  { "_id": 5, "name": "Michael", "address": "Valley 345"},
  { "_id": 6, "name": "Sandy", "address": "Ocean blvd 2"},
  { "_id": 7, "name": "Betty", "address": "Green Grass 1"},
  { "_id": 8, "name": "Richard", "address": "Sky st 331"},
  { "_id": 9, "name": "Susan", "address": "One way 98"},
  { "_id": 10, "name": "Vicky", "address": "Yellow Garden 2"},
  { "_id": 11, "name": "Ben", "address": "Park Lane 38"},
  { "_id": 12, "name": "William", "address": "Central st 954"},
  { "_id": 13, "name": "Chuck", "address": "Main Road 989"},
  { "_id": 14, "name": "Viola", "address": "Sideway 1633"}
]
# z=mycollection.insert_many(mylist) 


#find viene siendo como el select * en sql
# for x in mycollection.find():
# 	print(x)


#como segundo parametro de find se ponen que valores se quieren mostrar en la consulta
#si se pone en 1 se muestra la clave con 0 no se muestra
#si se especifica 1 o 0 en una clave y no el resto se le asignara al reato resectivamente 0 o 1
# for x in mycollection.find({},{ "address": 0, "edad": 0 }):
#   print(x)


#El primer parámetro de find es un filtro que relaciona una clave con un valor para realizar el filtrado
# filtro = { "name" : "Viola" } 
# query =  mycollection.find(filtro,{"name" : 1})
# for x in query:	
# 	print(x)


#Advanced query
#Se puede realizar un filtro utilizando expresiones regulares
filtro = {"name" : { "$regex" : "^S"}}
query = mycollection.find(filtro)
for x in query:
	print(x)

