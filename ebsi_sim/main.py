from fastapi import FastAPI, Request
from sqlmodel import Session

from ebsi_sim.api.v1.tnt import router as tntapp
from ebsi_sim.core.db import engine, session_ctx

app = FastAPI(root_path="/v1")
app.include_router(tntapp)


@app.middleware("http")
async def db_session_handler(request: Request, call_next):
    with Session(engine) as session:
        token = session_ctx.set(session)
        try:
            response = await call_next(request)
        finally:
            session_ctx.reset(token)
            session.close()
    return response