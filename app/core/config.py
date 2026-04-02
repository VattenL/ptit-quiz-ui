from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_NAME: str = "quiz_platform.db"

    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite:///./{self.DB_NAME}"

    model_config = {"env_file": ".env"}


settings = Settings()
