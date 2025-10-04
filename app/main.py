from fastapi import FastAPI
from app.api import ping, jobs   # 👈 include jobs router
from app.core.config import settings
from app.db.session import Base, engine
import app.db.models  # ensure Job model registered
from app.core.scheduler import start_scheduler, schedule_job
from app.db import crud, models
from app.db.session import SessionLocal
import logging


# Configure global logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

def create_app():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
    )

    # include routers
    app.include_router(ping.router)
    app.include_router(jobs.router)

    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all(bind=engine)

        # start scheduler
        sched = start_scheduler()

        # re-schedule jobs already in DB
        db = SessionLocal()
        try:
            jobs = db.query(models.Job).all()
            for j in jobs:
                schedule_job(j)
        finally:
            db.close()

    return app

logger = logging.getLogger(__name__)
app = create_app()





