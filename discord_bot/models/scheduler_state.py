from functools import cache
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pydantic import BaseModel, ConfigDict


class SchedulerState(BaseModel):
    current_scheduler: Optional[AsyncIOScheduler] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


@cache
def get_scheduler_state() -> SchedulerState:
    return SchedulerState()
