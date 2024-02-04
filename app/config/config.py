from os import getenv

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    # Service settings
    APP_PORT: int = int(getenv('APP_PORT', 8000))
    PATH_PREFIX: str = getenv('PATH_PREFIX', '/api/v1')

    # Database settings
    POSTGRES_DB: str = getenv('POSTGRES_DB', 'db')
    POSTGRES_USER: str = getenv('POSTGRES_USER', 'user')
    POSTGRES_PASSWORD: str = getenv('POSTGRES_PASSWORD', '12345')
    POSTGRES_PORT: int = int(getenv('POSTGRES_PORT', 5432))
    POSTGRES_HOST: str = getenv('POSTGRES_HOST', 'localhost')  # By default - localhost (for migration)

    # Redis
    REDIS_HOST: str = getenv('REDIS_HOST', 'app-redis')
    REDIS_PORT: int = int(getenv('REDIS_PORT', 6379))

    # In Docker?
    DOCKER: bool = bool(getenv('DOCKER', 0))

    def get_db_url(self) -> str:
        if self.DOCKER:
            postgres_host = self.POSTGRES_HOST
        else:
            postgres_host = 'localhost'
        return (f'postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
                f'@{postgres_host}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}')

    def get_db_url_async(self) -> str:
        return (f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
                f'@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}')


settings = Settings()
