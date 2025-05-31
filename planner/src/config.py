from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    LINEAR: str
    OPENAI: str

    model_config = SettingsConfigDict(env_file="local.env", env_file_encoding="utf-8")



config = Config()