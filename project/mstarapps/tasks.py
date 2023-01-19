

import shutil
import os
import json
import subprocess
from datetime import datetime

from celery import shared_task
from celery.utils.log import get_task_logger
from celery import chain

#from celery import current_app as current_celery_app
import mstar
from project.mstarapps.models import AppJob, JobStatus
from project import db, ext_celery


celery = ext_celery.celery
input_dir = "/home/kevin/w/mstar-webapp2/data-input"
output_dir = "/home/kevin/w/mstar-webapp2/data-output"
logger = get_task_logger(__name__)
mstar.Initialize()

def delaySimpleRpmJob(id: int, rpm: float, fluidHeight: float):

	onerr = onErrSig(id)

	chain(prepare_simpleRpmJob.s(id, rpm, fluidHeight).on_error(onerr), 
			gpu_RunCase.s(id).set(queue="gpu").set(immutable=True).on_error(onerr),
			gpu_RunPostLast.s(id).set(queue="gpu").set(immutable=True).on_error(onerr),
			setJobStatusTask.s(id, JobStatus.Completed.value).set(immutable=True)
			).delay()

def setJobStatus(id: int, status: JobStatus):
	try:        
		job: AppJob = db.session.query(AppJob).get(id)
		job.job_status = status
		
		if status in [ JobStatus.Completed, JobStatus.Error ]:
			job.completed = datetime.now()

		db.session.commit()
	except Exception as e:
		db.session.rollback()
		raise

def getJobStatus(id: int, status: JobStatus):	
	job: AppJob = db.session.query(AppJob).get(id)
	return job.job_status	

@celery.task()
def setJobStatusTask(id: int, status: int):
	setJobStatus(id, JobStatus(status) )

@celery.task()
def setJobStatusTaskOnError(request, exc, traceback, id=-1, status=JobStatus.Error.value):

	try:
		casePath = os.path.join(output_dir, str(id))
		if os.path.isdir(casePath):
			with open(os.path.join(casePath, "internal-errs.txt"), 'a') as fh:
				print('--\n\n{0} {1} {2}'.format(request.id, exc, traceback), file=fh)
	except:
		pass

	setJobStatus(id, JobStatus(status) )

def onErrSig(id):
	return setJobStatusTaskOnError.s(id=id, status=JobStatus.Error.value)

@celery.task()
def prepare_simpleRpmJob(id: int, rpm: float, fluidHeight: float):	
	job = db.session.query(AppJob).get(id)
	if job is None:
		raise ValueError("Job not found: {0}".format(id))

	casePath = os.path.join(output_dir, str(job.id))
	
	if not os.path.isdir(casePath):
		logger.info("creating case at " + casePath)
		os.makedirs(casePath)
	
	inputMsbFn = os.path.join(input_dir, "simpleRpmApp/simulationFreeSurface.msb")
	outputMsbFn = os.path.join(casePath, "job.msb")
	metaFn = os.path.join(casePath, "meta.json")
	metaData = dict(jobid=job.id, 
					name=job.app_name, 
					created=job.created.isoformat(),
					input_msb=inputMsbFn,
					output_msb=outputMsbFn,
					rpm=rpm,
					fluid_height=fluidHeight)

	with open (metaFn, 'w') as of:
		json.dump(metaData, of)
		
	logger.info("Loading msb: " + inputMsbFn)
	m = mstar.Load(inputMsbFn)    
		
	logger.info("Applying changes to msb")
	m.Get("Moving Body").Get("Rotation Speed").Value = str(rpm)
	m.Get("Fluid Height Box").Get("Fluid Height").Value = fluidHeight

	logger.info("Saving msb: " + outputMsbFn)
	m.Save(outputMsbFn)

	logger.info("Exporting case: " + casePath)
	m.Export(casePath)

@celery.task()
def gpu_RunCase(job_id):
	
	casePath = os.path.join(output_dir, str(job_id))

	gpuids = ["0"]
	gpuidarg = ",".join(gpuids)
	cmd = [ "mstar-cfd-mgpu", "-i", "input.xml", "-o", "out", "--force", "--gpu-ids=" + gpuidarg ]

	stdOutLogPath = os.path.join(casePath, "log-stdout.txt")
	stdErrLogPath = os.path.join(casePath, "log-stderr.txt")
	with open(stdOutLogPath, "w") as ostd:
		with open(stdErrLogPath, "w") as oerr:
			
			setJobStatus(job_id, JobStatus.Running)
			
			line = "*" * 40
			line += "\n"
			ostd.write("\n\n")
			ostd.write(line)
			ostd.write("Running command: {0}\n".format(" ".join(cmd)))
			ostd.write("Using GPUs: {0}\n".format(" ".join(gpuids)))
			ostd.write("Started: {0} \n".format(datetime.now().isoformat()))
			ostd.write(line)
			ostd.write("\n\n")
			ostd.flush()

			compl = subprocess.run(cmd, stdout=ostd, stderr=oerr, cwd=casePath)			

			ostd.write("\n\n")
			ostd.write(line)
			ostd.write("Ended: {0} \n".format(datetime.now().isoformat()))
			ostd.write("Process exit code: {0}\n".format(compl.returncode))
			ostd.write(line)			

			if compl.returncode != 0:
				logger.error("Process failed with exit code {0}".format(compl.returncode))
				raise ValueError("Process failed")
				

@celery.task()
def gpu_RunPostLast(job_id):

	# Todo - redirect log to file
	# Todo - capture errors? 
	import matplotlib
	matplotlib.use("Agg")
	casePath = os.path.join(output_dir, str(job_id))
	from mstarpypost.batch_post import CreateAllBatchConfig, run_post
	conf = CreateAllBatchConfig(casePath, 
									do_slice=True, 
									do_volume=False, 
									do_particle=False, 
									do_body=False, 
									always_show_particles=False,
									last_only=False)
	conf.auto_pdf_report = True
	conf.auto_stat_plots = True
	run_post(casePath, conf)



@celery.task()
def gpu_Test():
	logger.info("Hello World from gpu Test task")


@shared_task
def submit_app_job():
	pass