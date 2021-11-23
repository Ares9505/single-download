import pyrogram
import json
import jsonpickle
import time
import asyncio
import logging
import shutil
from pathlib import Path
import random
import os
import pymongo

def check_free_sessions():
	while True:
		start = time.time()
		with open("config.json","r") as file:
			config = json.load(file)
		free_sessions = [i for i in range(1,config["session quantity"]+1) if config[str(i)] == 0]
		if free_sessions:
			return free_sessions
		end = time.time()
		duration = end - start
		if duration > 18:
			#In this case duration will be none
			return free_sessions
		
def ask_for_media_and_download(
	config: dict,
	session_string: str ,
	 uri: str,
	 collection: pymongo.collection.Collection):	

	#BOT CHAT NAME 
	chat_name = "spotify_down_bot" # access only via web

	#CONNECT CLIENT
	client = pyrogram.Client(session_string, config["api_id"], config["api_hash"]) 
	client.start()

	#TO SEE SESSION OWNER
	logging.info(f'Username {client.get_me().username}')

	#CLEAN CHAT
	'''
		Avoid erase first 3 sms, it is the start bot indication
	'''
	messages = client.iter_history(chat_name, reverse = True)
	for index,message in enumerate(messages):
		if index > 2:
			client.delete_messages(chat_name,message.message_id)

	# #SENDING URI
	sms = "/download spotify:track:" + uri
	client.send_message(chat_name, sms)	

	#LOOKING MESSAGES
	messages = client.iter_history(chat_name, reverse = True)
	
	#GUARATEE MEDIA AVAILABLE
	no_media = True
	while(no_media):

		start = time.time()
		messages = client.iter_history(chat_name, reverse = True)
		logging.info("Waiting for download available")
		time.sleep(1)
		end = time.time()

		if len(messages) == 6 :
			#the media aparece en el sms 4 o el 5
			index = 4 if messages[4]['audio'] else 5
			logging.info(f'Media available. Title: {messages[index]['audio']['title']}')
			no_media = False

		#MINIMUN TIME TO FIND SONG 
		'''
			We can't permanently get message history cause an error raise up
		'''
		if end - start > 10:
			logging.warning(f'Error. No song founded for {uri}')
			update_database(collection, uri, state = "ERROR", path = "ERROR")
			return

	#DOWNLOAD SINGLE MEDIA
	for i in range(3):
		try:
			time.sleep(1)
			download_path = client.download_media(messages[index]['audio'])
			logging.info("Downloading media")
		except:
			logging.info(f'Attemp {i+1} to download media')
			if i + 1 == 3:
				logging.info("Media wasn't downloaded")
				download_path = None

	if download_path:
		shutil.move(download_path,f'audio/{Path(download_path).name}')
		final_path = os.getcwd() + f'/audio/{Path(download_path).name}'
		logging.info("Media available at : " + final_path)
		update_database(collection, "OK", final_path)
		return

	else:
		update_database(collection, uri, state = "ERROR", path ="ERROR")
		logging.info("Error during media download.")
		return


def set_session_state(config: dict, session_number: int):

	#IF IT IS ZERO TURN TO ONE IF IT IS ONE TURN TO ZERO
	''' Zero means free session One means bussy session'''
	config[str(session_number)] = int ( not config[str(session_number)] )
	
	with open("config.json", "w") as cfile:
		json.dump(config, cfile, indent = 3 )


def single_download(uri: str):
	logging.basicConfig(level = logging.INFO )

	with open("config.json","r") as config_file:
		config = json.load(config_file)

	if check_free_sessions():
		session_selected = random.choice(check_free_sessions())
		print(f'Session seleccionada: {session_selected}')
		
		#SET SESSION BUSSY
		set_session_state(config, session_selected)
		
		with open(f'sessions/session{session_selected}.txt') as sfile:
			session_string_selected = sfile.read()

		path = ask_for_media_and_download(config, session_string_selected, uri)

		#SET SESSION READY
		set_session_state(config, session_selected)

		return path

	else :
		logging.warning("Can't download this song cause all API sessions are bussy")
		return "Error. All single download API sessions are bussy"


def pending_uri(
	collection: pymongo.collection.Collection
	) -> dict:
	'''
		*Extract doc with mayor priority and state equal pending 
		*Update doc extracted with state =  Procesing
	'''	

	uri_doc = collection.find_one({"state": "PENDING"},sort = [("priority",-1)])

	if uri_doc:
		uri = uri_doc["uri"]
		uri_doc_id = {"uri" : uri}
		field_to_update = {"$set" : {"state": "PROCESING"}}
		collection.update_one( uri_doc_id, field_to_update)
		logging.info(f'Uri {uri} is being processed')
	
	else:
		uri = None
		logging.info("In loop, loocking for pending uri")
	return uri



def update_database(
	collection: pymongo.collection.Collection,
	uri: str,
	state: str,
	path: str ):

	field_to_update = {"$set" : {"state": state, "path": path}}
	collection.update_one( {"uri" : uri } , field_to_update)


#MAIN
def singleDownload():
	logging.basicConfig(level = logging.INFO )
	logger = logging.getLogger("singleDownload")

	with open("config.json","r") as config_file:
		config = json.load(config_file)


	logger.info("Connecting to MongoDB...")
	client = pymongo.MongoClient(config['db_conection'])
	collection = client[config['db_name']][config['collection_name']]			
	
	condition =True		
	while condition:
		session_free_list = check_free_sessions()
		if session_free_list:
			session_selected = random.choice(session_free_list)
			logger.info(f'Session seleccionada: {session_selected}')
		
			uri = pending_uri(collection)
			print(uri)
			if uri:
				
				#SET SESSION BUSSY					
				set_session_state(config, session_selected)

				with open(f'sessions/session{session_selected}.txt') as sfile:
					session_string_selected = sfile.read()

				path = ask_for_media_and_download(config, session_string_selected, uri,collection)
							
				#SET SESSION READY
				set_session_state(config, session_selected)


			time.sleep(2)


		condition = False	



if __name__ == "__main__":	
	# print(single_download("spotify:track:1BLfQ6dPXmuDrFmbdfW7Jl"))
	singleDownload()


'''
Tareas:
	*Cambiar por session_string la conexion del cliente x (storage_sessions.py)
	*Agregar seteo de estados del descagador x
	*Crear y llenar base de datos de prueba  x
	*Consulta a base de datos para ver si hay uris pendientes y extraer la de mayor prioridad x
	*Descargar uri pendiente si hay alguna sesion desocupada x
	*Tener en cuenta uri con dos medias para descargar (Esto no ocurre nunca)
	*Establecer lazo while true para que se chequee eternamente la base de  datos x
	*Hacer funcion que actualice la base de datos (Pendiente)

	*Llenar base de datos con path de la cancion descargada segun uri
	*Instalar telegra desktop para checar envio de sms
	*Agregar validacion de la uri
	*Agregar CCU sincrono
	
Notas:
	*Se debe cambiar en configuracion en config.json y poner la direccion para la conexion con la base de  datos,
	el nobre de la base de datos y la conexion a la hora de integrar con rey
'''
