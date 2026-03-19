from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Quiz Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "quiz_platform"
    DB_USER: str = "root"
    DB_PASSWORD: str = ""

    JWT_SECRET_KEY: str = "change_this_secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 10080

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
