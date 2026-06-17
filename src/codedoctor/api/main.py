from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from codedoctor.api.routers.doctor import doctor_router
from codedoctor.api.routers.engineer import engineer_router

app = FastAPI()

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(doctor_router)
app.include_router(engineer_router)
