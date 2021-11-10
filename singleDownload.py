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
	try:
		download_path = await client.download_media(media_message)
	except AttributeError:
		print("Song alredy exist in audio folder")
		return None
	return download_path



def ask_for_media_and_download(
	config: dict,
	session_string: str ,
	 uri: str):
	
	logging.basicConfig(level = logging.INFO )

	#BOT CHAT NAME 
	chat_name = "spotify_down_bot" # access only via web

	#CONNECT CLIENT
	client = pyrogram.Client(session_string, config["api_id"], config["api_hash"]) 
	client.start()

	#TO SEE SESSION OWNER
	client.get_me()

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
	
	shutil.move(download_path,f'audio/{Path(download_path).name}')
	final_path = os.getcwd() + f'/audio/{Path(download_path).name}'
	logging.info("Media available at : " + final_path)

	return final_path



def set_session_state(config: dict, session_number: int):

	#IF IT IS ZERO TURN TO ONE IF UT IS ONE TURN TO ZERO
	config[str(session_number)] = int ( not config[str(session_number)] )
	
	with open("config.json", "w") as cfile:
		json.dump(config, cfile, indent = 3 )




#Main
def single_download(uri: str):
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
		print("Can't download this song cause All API sessions are bussy")
		return "All single download API sessions are bussy"



if __name__ == "__main__":
	with open("config.json","r") as config_file:
		config = json.load(config_file)

	with open(f'sessions/session3.txt') as sfile:
			session_string_selected = sfile.read()

	ask_for_media_and_download(config, session_string_selected ,"/download spotify:track:6C62fl8x0vzwxPqay8twie")
	# set_session_state(config, 1)
	# print(single_download("/download spotify:track:6eDImMU0RbxxTWqlEzpcom"))
	# print(single_download("/download spotify:track:6C62fl8x0vzwxPqay8twie")
	

'''
Tareas:

	*Cambiar por session_string la conexion del cliente x
	*Agregar seteo de estados del descagador x
	*Agregar CCU sincrono
	
Notas:
	*Checar cual seria un valor idoneo para duration en check free session
'''
