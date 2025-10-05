from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.services.job_service import dummy_task
from app.db.session import SessionLocal
from app.db import crud
from functools import partial
import logging
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = None

def start_scheduler():
    global scheduler
    if scheduler:
        return scheduler
    scheduler = BackgroundScheduler()
    scheduler.start()
    logger.info("APScheduler started")
    return scheduler

def schedule_job(job, db_session_factory=SessionLocal):
    """Add or update a job in APScheduler."""
    job_id = f"job-{job.id}"

    # Remove existing job if already scheduled
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"♻️ Rescheduled job {job.id} ({job.name})")

    # Pick trigger type
    if job.schedule_type == "interval":
        trigger = IntervalTrigger(**job.schedule_config)
    elif job.schedule_type == "cron":
        trigger = CronTrigger(**job.schedule_config)
    else:
        raise ValueError(f"Unsupported schedule_type: {job.schedule_type}")

    job_func = partial(dummy_task, job.id, db_session_factory)
    sched_job = scheduler.add_job(job_func, trigger=trigger, id=job_id, replace_existing=True)

    crud.set_job_next_run(db_session_factory(), job.id, sched_job.next_run_time)
    logger.info(f"📅 Scheduled job {job.id} ({job.name}) [{job.schedule_type}] → next run at {sched_job.next_run_time}")


def remove_job(job_id: int):
    """Remove a job from APScheduler by ID."""
    job_key = f"job-{job_id}"
    if scheduler and scheduler.get_job(job_key):
        scheduler.remove_job(job_key)
        logger.info(f"🗑️ Removed job {job_id} from APScheduler")
