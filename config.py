from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    token_expiration_time: int
    no_auth: bool
    json_file_path: str

    model_config = SettingsConfigDict(env_file=".env")
