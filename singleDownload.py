import pyrogram
import json
import jsonpickle
import time
import asyncio
import logging
import shutil
from pathlib import Path
import random

def check_free_sessions():
	start = time.time()
	
	no_session_free = True
	
	while no_session_free:

		with open("config.json","r") as file:
			config = json.load(file)
		
		free_sessions = [i for i in range(1,config["session quantity"]+1) if config[str(i)] == 0]
		
		if free_sessions:
			return free_sessions
		
		end = time.time()
		duration =  end - start

		if duration > 2:
			return free_sessions

async def download_media(
		client: pyrogram.client.Client,
		media_message: pyrogram.types.Message): 

	download_path = await client.download_media(media_message)
	return download_path



def ask_for_media_and_download(session_string: str , uri: str):
	logging.basicConfig(level = logging.INFO )

	with open("config.json","r") as config_file:
		config = json.load(config_file)

	#BOT CHAT NAME 
	chat_name = "spotify_down_bot" # access only via web

	#CONNECT CLIENT
	client = pyrogram.Client(session_string, config["api_id"], config["api_hash"]) 
	client.start()

	#CLEAN CHAT
	'''
		Avoid erase first 3 sms, it is the start bot indication
	'''
	messages = client.iter_history(chat_name, reverse = True)
	for index,message in enumerate(messages):
		if index > 2:
			client.delete_messages(chat_name,message.message_id)

	# #SENDING URI
	client.send_message(chat_name, uri)	

	#LOOKING MESSAGES
	messages = client.iter_history(chat_name, reverse = True)
	
	#GUARATEE MEDIA AVAILABLE
	while(len(messages) < 6):
		messages = client.iter_history(chat_name, reverse = True)
		print(len(messages))
		logging.info("Waiting for download available")

	#DOWNLOAD SINGLE MEDIA
	download_path = asyncio.get_event_loop().run_until_complete(download_media(client,messages[5]['audio']))
	logging.info("Media available at : " + download_path)

	shutil.move(download_path,f'audio/{Path(download_path).name}')


def single_download(uri: str):

	if check_free_sessions():
		session_selected = random.choice(check_free_sessions())
		print(f'Session seleccionada: {session_selected}')

		ask_for_media_and_download(session_selected)

	else :
		print("Can't download this song cause All API sessions are bussy")

if __name__ == "__main__":
	single_download("/download spotify:track:6C62fl8x0vzwxPqay8twie")
	# ask_for_media_and_download("/download spotify:track:6C62fl8x0vzwxPqay8twie")
	#We can't use this method cause througth copyrigth error
	#result = client.get_inline_bot_results(bot = chat_name, query = "/download spotify:track:6C62fl8x0vzwxPqay8twie")
	#print(result)

'''
Tareas:

	*Cambiar por session_string la conexion del cliente
	*Agregar seteo de estados del descagador
	*Agregar CCU sincrono
	
Notas:
	*Checar cual seria un valor idoneo para duration en check free session
'''
