#pip install fastapi uvicorn
from singleDownload import *

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
	return {"Hello": "World"}


@app.get("/{uri}")
def read_uri( uri: str):
	try:
		response = single_download(uri)
		return {"Path": response}
	except:
		return {"Path":"Single download API error"} 
	

#tap uvicorn api:app --reload for start api