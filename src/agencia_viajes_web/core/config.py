from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_host: str = "localhost"
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_password: str = "password"
    db_port: str = "5432"

    secret_key: str = "cookie_secret_key"
    session_max_age: int = 3600

    model_config = SettingsConfigDict(env_file='.env', extra="ignore")

settings = Settings()