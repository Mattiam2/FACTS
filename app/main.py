from fastapi import FastAPI
from app.tnt import router as tntapp
app = FastAPI(root_path="/v1")
app.include_router(tntapp)