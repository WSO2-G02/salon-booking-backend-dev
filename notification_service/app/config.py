from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_connection_string: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    smtp_email: str
    smtp_app_password: str

    class Config:
        env_file = ".env"

settings = Settings()
