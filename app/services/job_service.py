from datetime import datetime
from sqlalchemy.orm import Session
from app.db import crud
import logging

logger = logging.getLogger(__name__)

def dummy_task(job_id: int, db_session_factory):
    """This is the job APScheduler runs."""
    db: Session = db_session_factory()
    try:
        now = datetime.utcnow()
        logger.info(f"Running job {job_id} at {now}")
        # update last_run_at
        crud.update_job_run_timestamps(db, job_id, last_run=now)
    except Exception as e:
        logger.error(f"Error running job {job_id}: {e}")
    finally:
        db.close()
