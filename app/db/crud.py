from sqlalchemy.orm import Session
from app.db import models
from app.schemas.job import JobCreate, JobUpdate
from datetime import datetime

def create_job(db: Session, job: JobCreate):
    db_job = models.Job(
        name=job.name,
        schedule_type=job.schedule_type,
        schedule_config=job.schedule_config,
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_job(db: Session, job_id: int):
    return db.query(models.Job).filter(models.Job.id == job_id).first()

def list_jobs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Job).offset(skip).limit(limit).all()

def update_job(db: Session, job_id: int, job_update: JobUpdate):
    job = get_job(db, job_id)
    if not job:
        return None
    if job_update.name is not None:
        job.name = job_update.name
    if job_update.schedule_type is not None:
        job.schedule_type = job_update.schedule_type
    if job_update.schedule_config is not None:
        job.schedule_config = job_update.schedule_config

    db.commit()
    db.refresh(job)
    return job

def delete_job(db: Session, job_id: int):
    job = get_job(db, job_id)
    if not job:
        return None
    db.delete(job)
    db.commit()
    return job


def update_job_run_timestamps(db: Session, job_id: int, last_run: datetime, next_run: datetime = None):
    job = get_job(db, job_id)
    if not job:
        return None
    job.last_run_at = last_run
    if next_run:
        job.next_run_at = next_run
    db.commit()
    db.refresh(job)
    return job

def set_job_next_run(db: Session, job_id: int, next_run):
    job = get_job(db, job_id)
    if not job:
        return None
    job.next_run_at = next_run
    db.commit()
    db.refresh(job)
    return job