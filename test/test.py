import mutagen
import os

filePath = os.getcwd() + "/audio.mp3"
tag = mutagen.File(filePath, easy= True)
print(tag)
print(tag['artist'])
print(tag['albumartist'])

