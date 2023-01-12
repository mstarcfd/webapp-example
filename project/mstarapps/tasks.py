

import shutil
import os
import json

from celery import shared_task
from celery.utils.log import get_task_logger
#from celery import current_app as current_celery_app
import mstar
from project.mstarapps.models import AppJob
from project import db, ext_celery


celery = ext_celery.celery
input_dir = "/home/kevin/w/mstar-webapp2/data-input"
output_dir = "/home/kevin/w/mstar-webapp2/data-output"
logger = get_task_logger(__name__)
mstar.Initialize()

@celery.task()
def prepare_simpleRpmJob(rpm: float):
    
    job = None
    try:        
        job = AppJob(app_name="Simple RPM Job")
        db.session.add(job)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise

    if job is None:
        raise ValueError("job is null")

    casePath = os.path.join(output_dir, str(job.id))
    
    if not os.path.isdir(casePath):
        logger.info("creating case at " + casePath)
        os.makedirs(casePath)
    
    inputMsbFn = os.path.join(input_dir, "simpleRpmApp/simulation.msb")
    outputMsbFn = os.path.join(casePath, "job.msb")
    metaFn = os.path.join(casePath, "meta.json")
    metaData = dict(jobid=job.id, 
                    name=job.app_name, 
                    created=job.created.isoformat(),
                    input_msb=inputMsbFn,
                    output_msb=outputMsbFn,
                    rpm=rpm)

    with open (metaFn, 'w') as of:
        json.dump(metaData, of)
        
    logger.info("Loading msb: " + inputMsbFn)
    m = mstar.Load(inputMsbFn)    

    logger.info("Applying changes to msb")
    m.Get("Moving Body").Get("Rotation Speed").Value = str(rpm)

    logger.info("Saving msb: " + outputMsbFn)
    m.Save(outputMsbFn)

    logger.info("Exporting case: " + casePath)
    m.Export(casePath)




@shared_task
def submit_app_job():
    pass