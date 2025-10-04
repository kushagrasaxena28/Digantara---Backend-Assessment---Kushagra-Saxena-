# Scheduler Service
## Stage 1: Run basic server
1. Install dependencies:
   pip install -r requirements.txt

2. Run:
   uvicorn app.main:app --reload --port 5000

3. Test:
   curl http://127.0.0.1:5000/ping
   → {"message": "pong"}

## Stage 2: Run the Project :
1. Clone the Repo :
   git clone <your_repo_link_here>
   cd scheduler_service

2. Create a virtual environment( optional ) :
   python3 -m venv .venv
   source .venv/bin/activate

3. Install dependencies:
   pip install -r requirements.txt

4. Run:
   uvicorn app.main:app --reload --port 5000
   ## Expected Output :
      Uvicorn running on http://127.0.0.1:5000
5. Testing :
   ## schedule a job to run every 10 seconds :
      curl -X POST http://127.0.0.1:8000/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "every-10-sec",
    "schedule_type": "interval",
    "schedule_config": {"seconds": 10}
  }'
   ## View all jobs:
      curl http://127.0.0.1:8000/jobs/
   ## Update a job:
      curl -X PUT http://127.0.0.1:8000/jobs/1 \
  -H "Content-Type: application/json" \
  -d '{"schedule_config": {"seconds": 20}}'
   ## Delete a job:
      curl -X DELETE http://127.0.0.1:8000/jobs/1
   ## check job runs in DB ( If sqlite3 is installed ):
      sqlite3 jobs.db "SELECT id, name, last_run_at, next_run_at FROM jobs;"

      


# One Pager – Scheduler Microservice (Digantara Backend Assignment) :

So the project I built is a small backend microservice that lets users create and manage jobs that run automatically based on a schedule.
I used FastAPI for the APIs, SQLAlchemy + SQLite for the database (can switch to Postgres later), and APScheduler for the actual scheduling logic.

The idea is simple — when you add a job through POST /jobs, it gets stored in the DB and APScheduler automatically starts running it in the background.
We can also list all jobs by either sending a GET /jobs request to get all the jobs or GET /jobs/{job_id} to get a particular job, we can update them by sending a PUT /jobs/{job_id} (which reschedules the job), or delete them by sending a DELETE request to /jobs/{job_id} (which removes it from both APScheduler and DB).
Jobs can be scheduled using either interval (every x seconds/minutes/hours) or cron (specific times like every Monday at 9am).

The job logic itself is dummy right now — it just logs the execution and updates the last_run_at in the DB, but in the real world it could be sending emails, crunching data, etc.

# How we can improve this solution :

Right now it’s a single FastAPI + APScheduler process running everything.

## Some improvements that would make it production ready :

1. Switching from SQLite to PostgreSQL for proper concurrency and durability.

2. Using SQLAlchemyJobStore or a Redis-backed jobstore for APScheduler so jobs persist across restarts.

3. Splitting the system into two parts:

4. API service → only handles user requests & writes jobs to DB.

5. Scheduler worker → reads from DB and actually runs the jobs.

6. Adding an async queue (Redis / RabbitMQ) to offload heavy jobs.

7. Exposing internal metrics for job failures, execution time, etc.

## Maybe adding a paused flag to jobs so users can temporarily disable scheduling without deleting.

# How we would scale this to handle 10k users & 6k req/min :

Scaling this mainly means separating responsibilities and making things distributed.
Roughly this is how I’d do it:

## Database :

1. Moving to a central Postgres instance.

2. All services (API, scheduler) connect to it for job details.

3. Using read replicas if DB load gets high (a common practice in my previous company for read-heavy queries).

## Job Queue / Worker System :

1. Adding something like Redis Queue (RQ) or Celery. The scheduler just pushes due jobs into the queue, and multiple worker instances pick up and execute the jobs.

2. We can scale horizontally by adding more workers.

## Microservices Split :

1. API Service → handles CRUD, validation, etc. (currently doing the same in the project).

2. Scheduler Service → one leader instance (using Redis or DB lock for election) haven’t done this before but it’s a good production practice.

3. Worker Services → stateless, can scale up/down easily.

# Load Balancing & Caching :

1. Adding an API gateway (NGINX / Traefik) to route requests (a standard practice).

2. Using Redis to cache frequent GET /jobs calls to reduce DB hits (a common and effective use case).

## Monitoring & Observability :

1. Using Prometheus + Grafana or similar for job metrics and latency.

2. Logging job execution details for debugging and analytics.

## Deployment & Infra :

1. Running everything in Docker containers.

2. Deploying on Kubernetes.

3. Autoscaling worker pods based on queue length.

4. Scheduler pod should be a singleton (only one active instance).


# Final Thoughts :
The version I built is simple and reliable enough for a POC — single process, in-memory scheduler, persistent DB, easy APIs.
If we were to scale this up for production, the main thing would be to split responsibilities (API, scheduler, workers), use queues, and make scheduling distributed-safe.

# Basically:
One service to talk to users, one to plan jobs, and many to do the work.

