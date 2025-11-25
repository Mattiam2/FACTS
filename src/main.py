from fastapi import FastAPI
from src.tnt import app as tntapp
app = FastAPI()
app.mount("/track-and-trace", tntapp)