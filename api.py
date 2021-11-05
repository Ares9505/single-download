#pip install fastapi uvicorn

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
	return {"Hello": "World"}


@app.get("/uri/{uri}")
def read_uri( uri: str):
	

#tap uvicorn api:app --reload for start api