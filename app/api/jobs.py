from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.db import crud
from app.schemas.job import JobCreate, JobOut, JobUpdate
from app.scheduler.scheduler import start_scheduler, schedule_job, remove_job

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.post("/", response_model=JobOut, status_code=201)
def create_job(job: JobCreate, db: Session = Depends(get_db)):
    new_job = crud.create_job(db, job)
    start_scheduler()
    schedule_job(new_job)
    return new_job

@router.get("/", response_model=List[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    return crud.list_jobs(db)

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    db_job = crud.get_job(db, job_id)
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@router.put("/{job_id}", response_model=JobOut)
def update_job(job_id: int, job_update: JobUpdate, db: Session = Depends(get_db)):
    updated = crud.update_job(db, job_id, job_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Job not found")

    start_scheduler()
    schedule_job(updated)   # re-schedule in APScheduler
    return updated

@router.delete("/{job_id}", response_model=JobOut)
def delete_job(job_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_job(db, job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")

    remove_job(job_id)      # remove from APScheduler too
    return deleted

