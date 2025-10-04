from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.session import Base

class Job(Base):
    __tablename__: str = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    schedule_type = Column(String(50), nullable=False)   # e.g. interval / cron
    schedule_config = Column(JSON, nullable=False)       # JSON config
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
