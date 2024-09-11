from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from API_SCRIPTS.Facebook_API import reports_which_is_active
from Database.database import db

from .logging_settings import scheduler_logger

scheduler = AsyncIOScheduler()


def round_time(dt):
    round_to = 10
    seconds = (dt - dt.min).seconds
    rounding = (seconds + round_to * 30) // (round_to * 60) * (round_to * 60)
    return dt + timedelta(0, rounding - seconds)


async def add_job(job_id, time):
    db.query(f"DELETE FROM scheduled_jobs WHERE job_id LIKE '{job_id}%'")
    if ':' in time:
        hour, minute = time.split(':')
    else:
        hour, minute = time.split('.')
    time_1 = f'{hour}:{minute}'
    db.query(query="INSERT INTO scheduled_jobs (job_id, time) VALUES (%s, %s) "
                   "ON CONFLICT (job_id) DO UPDATE SET time = EXCLUDED.time",
             values=(job_id, time_1))


    scheduler_logger.info(f'Add job "{job_id}" complete')
    try:
        await load_jobs()
    except:
        pass


async def get_jobs():
    return db.query(query='SELECT job_id, time FROM scheduled_jobs ORDER BY job_id', fetch='fetchall')


async def all_acc_reports_job(job_id):
    try:
        await reports_which_is_active()
        scheduler_logger.info(f"Job executed: {job_id} at {datetime.now()}")
    except:
        pass


async def load_jobs():
    scheduled_jobs = await get_jobs()
    try:
        for job_id, time in scheduled_jobs:
            if ':' in time:
                hour, minute = time.split(':')
            elif '.' in time:
                hour, minute = time.split('.')
            else:
                scheduler_logger.error(f"Invalid time format for job {job_id}: {time}")
                continue
            scheduler.add_job(all_acc_reports_job, 'cron', hour=hour, minute=minute, args=[job_id],
                              id=job_id, replace_existing=True)
        scheduler_logger.info('Jobs loaded correctly.')
    except Exception as _ex:
        scheduler_logger.error(f'Failed to load jobs\n{_ex}')
