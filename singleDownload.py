import pyrogram
import json
import jsonpickle
import time
import asyncio

async def download_media(media_message): 
	download_path = await client.download_media(media_message)
	print(download_path)


def ask_for_media():
	with open("config.json","r") as config_file:
	config = json.load(config_file)

	#BOT CHAT NAME 
	chat_name = "spotify_down_bot" # access only via web

	#CONNECT CLIENT
	client = pyrogram.Client("my_account", config["api_id"], config["api_hash"]) 
	client.start()

	#CLEAN CHAT
	'''
		Avoid erase first sms, it is the start bot 
	'''
	messages = client.iter_history(chat_name, reverse = True)
	for index,message in enumerate(messages):
		if index > 0:
			client.delete_messages(chat_name,message.message_id)

	#SENDING URI
	client.send_message(chat_name, "/download spotify:track:6C62fl8x0vzwxPqay8twie")	



if __name__ == "__main__":
	# api_id = 8138563
	# api_hash = "ae1b0ed21810912df1a6280c5bd016b5"



	'''
		GETING MESSAGES AND DELITING ALL
			*Most left 3 sms at leats for let the bot running
	'''
	messages = client.iter_history(chat_name)
	# list_message_ids = []
	for message in messages:
		print(message.text)
	# 	if message['audio']:
	# 		print("Message with audio ", message.message_id)
	# 		asyncio.run(download_media(message))

		# dic_message = json.loads(jsonpickle.encode(message))
		# message_id = dic_message["py/state"]["message_id"] #dic_message["py/tuple"][1]["py/state"]["message_id"]
		# print(message_id)
		# print(dic_message['audio'])
		# try:
		# 	asyncio.run(download_media(message))
		# 	print("media descargada")
		# except:
		# 	print("No media ")
		#client.delete_messages(chat_name,message_id)

	#We can't use this method cause througth copyrigth error
	#result = client.get_inline_bot_results(bot = chat_name, query = "/download spotify:track:6C62fl8x0vzwxPqay8twie")
	#print(result)