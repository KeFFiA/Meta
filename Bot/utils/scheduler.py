from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from API_SCRIPTS.Facebook_api import reports_which_is_active
from Database.database import db

from .logging_settings import scheduler_logger

scheduler = AsyncIOScheduler()


def round_time(dt):
    round_to = 10
    seconds = (dt - dt.min).seconds
    rounding = (seconds + round_to * 30) // (round_to * 60) * (round_to * 60)
    return dt + timedelta(0, rounding - seconds)


async def add_job(job_id, date_list):
    count = 1
    db.query(query="INSERT INTO jobs (job_id) VALUES (%s) ON CONFLICT (job_id) DO NOTHING", values=(job_id,))
    for date in date_list:
        time = date.split(':')
        hour, minute = time
        print(hour, minute)
        job = f'{job_id}_{count}'
        db.query(query="INSERT INTO scheduled_jobs (job_id, hour, minute) VALUES (%s, %s, %s) "
                       "ON CONFLICT (job_id) DO UPDATE SET hour = EXCLUDED.hour, minute = EXCLUDED.minute",
                       values=(job, hour, minute))

        count += 1

    scheduler_logger.info(f'Add job "{job_id}" complete')
    try:
        await load_jobs()
    except:
        pass


async def get_jobs():
    return db.query(query='SELECT job_id, hour, minute FROM scheduled_jobs ORDER BY job_id', fetch='fetchall')


async def all_acc_reports_job(job_id):
    try:
        await reports_which_is_active()
        scheduler_logger.info(f"Job executed: {job_id} at {datetime.now()}")
    except:
        pass


async def load_jobs():
    scheduled_jobs = await get_jobs()
    try:
        for job_id, hour, minute in scheduled_jobs:
            scheduler.add_job(all_acc_reports_job, 'cron', hour=hour, minute=minute, args=[job_id],
                              id=job_id, replace_existing=True)
        scheduler_logger.info('Jobs loaded correctly.')
    except:
        pass
