from fastapi import FastAPI

from codedoctor.api.routers.doctor import doctor_router
from codedoctor.api.routers.engineer import engineer_router

app = FastAPI()

app.include_router(doctor_router)
app.include_router(engineer_router)
