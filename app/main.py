from fastapi import FastAPI
import logging

from app.database import engine, Base, create_db
from app.routes import auth
from app.routes import product as product_router  
from app.models import order
from app.routes import order


app = FastAPI()

create_db()

@app.get("/")
async def root():
    return {"status": "ok"}

app.include_router(auth.router)
app.include_router(product_router.router) 
app.include_router(order.router) 

@app.on_event("startup")
async def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
        logging.info("DB tables created/verified")
    except Exception as e:
        logging.error("DB connection failed: %s", e)