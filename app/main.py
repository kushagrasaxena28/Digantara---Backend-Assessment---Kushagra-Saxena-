from fastapi import FastAPI
from app.api import ping, jobs
from app.db.session import Base, engine
from app.scheduler.scheduler import start_scheduler, schedule_job
from app.db import models
from app.db.session import SessionLocal
import logging


# Configure global logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

def create_app():
    app = FastAPI(
        title="Schedling Service",
        version="0.1.0",
    )

    # include routers
    app.include_router(ping.router)
    app.include_router(jobs.router)

    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all(bind=engine)

        # start scheduler
        start_scheduler()

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





