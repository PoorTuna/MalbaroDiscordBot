import os
from functools import cache

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, JsonConfigSettingsSource


class TokenConfig(BaseSettings):
    discord_token: str
    wavespeed_tokens: list[str]

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        config_path = os.getenv("TOKEN_CONFIG_PATH")
        if not config_path:
            raise ValueError("TOKEN_CONFIG_PATH environment variable is not set.")
        return (JsonConfigSettingsSource(settings_cls, json_file=config_path),)


@cache
def get_token_config(*args, **kwargs):
    return TokenConfig(*args, **kwargs)
