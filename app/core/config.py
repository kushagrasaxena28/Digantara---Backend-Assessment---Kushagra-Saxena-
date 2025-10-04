from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME : str = "Schedling Service"
    VERSION : str = "0.1.0"

    class Config:
        env_file = ".env"

settings = Settings()