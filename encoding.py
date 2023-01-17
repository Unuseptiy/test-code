from fastapi import FastAPI
from pydantic import BaseModel
from urllib.parse import quote_plus

app = FastAPI()


# Path param
@app.get('/path/{url:path}')
def encode_path_url(url: str):
    return {'encoded_url': quote_plus(quote_plus(url))}


# Body param
class Url(BaseModel):
    path: str


@app.post('/path')
def encode_body_url(url: Url):
    return {'url': quote_plus(quote_plus(url.path))}


# Query param
@app.get('/path')
def encode_query_url(url: str):
    return {'url': quote_plus(quote_plus(url))}
