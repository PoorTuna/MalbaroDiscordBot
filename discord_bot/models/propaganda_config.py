import logging
import os
from functools import cache
from json import dump
from pathlib import Path

from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, JsonConfigSettingsSource

logger = logging.getLogger(__name__)


class PropagandaSchedulerTimeConfig(BaseModel):
    hour: int = Field(ge=0, lt=24)
    minute: int = Field(ge=0, lt=60)


class PropagandaSchedulerConfig(BaseModel):
    time: PropagandaSchedulerTimeConfig
    timezone: str
    poster_output_channel_id: int
    voice_channel_id: int
    youtube_playlist_url: str
    steam_ids: list[int]
    cs2_alert_video_url: str


class PropagandaConfig(BaseSettings):
    propaganda_scheduler: PropagandaSchedulerConfig
    text_prompt: str = Field(
        default="Generate a short, inspiring slogan for a propaganda poster about technology and progress")
    poster_caption: str = Field(default="A True Malborian Culture Piece:")
    max_retries: int = Field(ge=1, le=10, default=3)
    steam_api_key: str

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        config_path = os.getenv("PROPAGANDA_CONFIG_PATH")
        if not config_path:
            raise ValueError("PROPAGANDA_CONFIG_PATH environment variable is not set.")
        return (JsonConfigSettingsSource(settings_cls, json_file=config_path),)


def save_settings_to_file(settings: PropagandaConfig, path: str | Path = os.getenv("PROPAGANDA_CONFIG_PATH")) -> None:
    path = Path(path)
    with path.open("w", encoding="utf-8") as f:
        dump(settings.model_dump(), f, indent=4)


@cache
def get_propaganda_config(*args, **kwargs):
    return PropagandaConfig(*args, **kwargs)
