#pip install fastapi uvicorn
from singleDownload import *

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
	return {"Hello": "World"}


@app.get("/{uri}")
def read_uri( uri: str):
	response = single_download(uri)
	return {"Path": response}


#tap uvicorn api:app --reload for start api