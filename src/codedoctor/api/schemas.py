from pydantic import BaseModel


class DoctorRequest(BaseModel):
    root_dir: str
    user_prompt: str


class EngineerRequest(BaseModel):
    root_dir: str
    user_prompt: str
