from os import getenv

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    APP_PORT: int = int(getenv('APP_PORT', 8000))
    POSTGRES_DB: str = getenv('POSTGRES_DB', 'db')
    POSTGRES_USER: str = getenv('POSTGRES_USER', 'user')
    POSTGRES_PASSWORD: str = getenv('POSTGRES_PASSWORD', '12345')
    POSTGRES_PORT: int = int(getenv('POSTGRES_PORT', 5432))
    POSTGRES_HOST: str = getenv('POSTGRES_HOST', 'app-db')
