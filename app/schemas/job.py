from pydantic import BaseModel, root_validator
from typing import Optional, Dict, Any
from datetime import datetime

class JobBase(BaseModel):
    name: str
    schedule_type: str   # "interval" or "cron"
    schedule_config: Dict[str, Any]

class JobCreate(JobBase):
    @root_validator
    def validate_schedule_config(cls, values):
        st = values.get("schedule_type")
        config = values.get("schedule_config")
        if st == "interval":
            # must have at least one of seconds/minutes/hours
            if not any(k in config for k in ["seconds", "minutes", "hours"]):
                raise ValueError("interval jobs need seconds/minutes/hours")
        elif st == "cron":
            # must have at least one cron field
            if not any(k in config for k in ["minute", "hour", "day", "day_of_week", "month"]):
                raise ValueError("cron jobs need at least one cron field")
        else:
            raise ValueError("schedule_type must be 'interval' or 'cron'")
        return values

class JobUpdate(BaseModel):
    name: Optional[str] = None
    schedule_type: Optional[str] = None
    schedule_config: Optional[Dict[str, Any]] = None

class JobOut(JobBase):
    id: int
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]

    class Config:
        orm_mode = True
