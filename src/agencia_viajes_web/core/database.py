from pydantic import computed_field
from urllib.parse import quote_plus
from .config import settings

class Database():
    def __init__(self) -> None:
        self.__settings = settings

    @computed_field
    @property
    def database_url(self) -> str:
        encoded_pass = quote_plus(settings.db_password)
        return f"postgresql://{settings.db_user}:{encoded_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

database = Database()