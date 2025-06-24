from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    token_expiration_time: int
    no_auth: bool
    json_file_path: str
    access_token_expires_minutes: int
    default_user_email: str
    default_user_password: str
    default_user_device_token: str
    firebase_credentials_path: str
    default_pet_name: str
    default_pet_breed: str
    default_pet_color: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
