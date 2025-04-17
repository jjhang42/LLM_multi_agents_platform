from pydantic import BaseSettings

class Settings(BaseSettings):
    BROKER_TYPE: str = "nats"
    NATS_HOST: str = "nats://localhost:4222"
    REDIS_HOST: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"

settings = Settings()
