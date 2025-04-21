from functools import cache
from threading import Thread
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class BotState(BaseModel):
    status: str = Field(default="Not started",)
    thread: Optional[Thread] = None
    steam_thread: Optional[Thread] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)
@cache
def get_bot_state() -> BotState:
    return BotState()
