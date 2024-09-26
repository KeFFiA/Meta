import json
import os.path
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from API_SCRIPTS.Facebook_API import reports_which_is_active
from API_SCRIPTS.GetCourse_API import getcourse_report
from API_SCRIPTS.eWebinar_API import get_all_registrants
from Database.database import db

from .logging_settings import scheduler_logger

try:
    path = os.path.abspath('./Bot/temp/last_update.json')
    open(path).close()
except Exception as _ex:
    scheduler_logger.critical(f'Error opening last_update.json: {_ex}')

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


async def facebook_reports_job(job_id):
    try:
        await reports_which_is_active()
        scheduler_logger.info(f"Job executed: {job_id} at {datetime.now()}")

        record = {'Facebook': f'Последнее обновление <b>{datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}</b>'}

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = {}

        for key, value in record.items():
            data[key] = value

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        scheduler_logger.error(f"Error executing job {job_id}: {e}")


async def ewebinar_reports_job(job_id):
    try:
        await get_all_registrants()
        scheduler_logger.info(f"Job executed: {job_id} at {datetime.now()}")

        record = {'eWebinar': f'Последнее обновление <b>{datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}</b>'}

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = {}

        for key, value in record.items():
            data[key] = value

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        scheduler_logger.error(f"Error executing job {job_id}: {e}")


async def getcourse_reports_job(job_id):
    try:
        await getcourse_report()
        scheduler_logger.info(f"Job executed: {job_id} at {datetime.now()}")

        record = {'GetCourse': f'Последнее обновление <b>{datetime.now().strftime("%m/%d/%Y - %H:%M:%S")}</b>'}

        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        else:
            data = {}

        for key, value in record.items():
            data[key] = value

        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        scheduler_logger.error(f"Error executing job {job_id}: {e}")


async def get_jobs():
    return db.query(query='SELECT job_id, time FROM scheduled_jobs ORDER BY job_id', fetch='fetchall')

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

            if job_id.startswith('facebook_'):
                scheduler.add_job(facebook_reports_job, 'cron', hour=hour, minute=minute, args=(job_id,),
                                  id=job_id, replace_existing=True)
            elif job_id.startswith('ewebinar_'):
                scheduler.add_job(ewebinar_reports_job, 'cron', hour=hour, minute=minute, args=(job_id,),
                                  id=job_id, replace_existing=True)
            elif job_id.startswith('getcourse_'):
                scheduler.add_job(getcourse_reports_job, 'cron', hour=hour, minute=minute, args=(job_id,),
                                  id=job_id, replace_existing=True)

        scheduler_logger.info('Jobs loaded correctly.')
    except Exception as _ex:
        scheduler_logger.error(f'Failed to load jobs\n{_ex}')

