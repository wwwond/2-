from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.main import router as main_router
import models
from database import Base, engine

app=FastAPI()


app.add_middleware(
     CORSMiddleware,
     allow_origins=["*"],
     allow_credentials=True,
     allow_methods=["*"],
     allow_headers=["*"],
)

app.include_router(main_router)