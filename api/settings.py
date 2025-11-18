from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    BALLDONTLIE_API_KEY: str

    class Config:
        env_file = ".env"   # faz o pydantic ler o .env automaticamente

settings = Settings()
