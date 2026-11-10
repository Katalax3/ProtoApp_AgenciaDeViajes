from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from urllib.parse import quote_plus


class Settings(BaseSettings):
    db_host: str = "localhost"
    db_name: str = "postgres"
    db_user: str = "postgres"
    db_password: str = "password"
    db_port: str = "5432"

    @computed_field
    @property
    def database_url(self) -> str:
        encoded_pass = quote_plus(self.db_password)
        return f"postgresql://{self.db_user}:{encoded_pass}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    model_config = SettingsConfigDict(env_file='.env', extra="ignore")

settings = Settings()

pool = ConnectionPool(settings.database_url, kwargs={"row_factory":dict_row}, max_size=10, min_size=2)