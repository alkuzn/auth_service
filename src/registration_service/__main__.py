import uvicorn

from registration_service.api.handles import app
from registration_service.config import Config
from pydantic import BaseModel, EmailStr

if __name__ == "__main__":
    uvicorn.run("registration_service:app", reload=True, port=1234)
