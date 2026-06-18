from pydantic import BaseModel


class BaseRequest(BaseModel):
    root_dir: str
    search_dir: str | None = None
    test_dir: str | None = None
    max_retries: int | None = None
    include_dot: bool | None = None
    ignore: set[str] | list[str] | str | None = None
    strong_model: str | None = None
    weak_model: str | None = None


class DoctorRequest(BaseRequest):
    user_prompt: str | None = None


class EngineerRequest(BaseRequest):
    user_prompt: str


class ContextSchema(BaseModel):
    search_dir: str
    test_dir: str
    max_retries: int
    include_dot: bool
    ignore: set[str] | list[str] | str
    strong_model: str
    weak_model: str
