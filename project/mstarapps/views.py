
from .forms import SimpleRpmForm
from flask import request, flash, redirect, url_for, render_template
from . import app_blueprint
from .models import AppJob
from .tasks import delaySimpleRpmJob

import os
from project import db
from sqlalchemy import desc

output_dir = "/home/kevin/w/mstar-webapp2/data-output"

@app_blueprint.route('/simple', methods=['GET', 'POST'])
def simpleRpmForm():
    form = SimpleRpmForm()
    if form.validate_on_submit():
        
        jobid = -1
        try:        
            job = AppJob(app_name="Simple RPM Job")
            db.session.add(job)
            db.session.commit()

            jobid = job.id
        except Exception as e:
            db.session.rollback()
            raise

        delaySimpleRpmJob(jobid, form.rpm.data)

        return redirect(url_for("mstarapp.manage_jobs"))
    return render_template("simpleRpmForm.html", form=form)

@app_blueprint.route('/manage_jobs', methods=['GET'])
def manage_jobs():
    appJobs = db.session.execute(db.select(AppJob).order_by(AppJob.created.desc())).scalars()

    return render_template("manage_jobs.html", jobs=appJobs)

@app_blueprint.route('/', methods=['GET'])
def dashboard():
    return render_template("dashboard.html")


@app_blueprint.route('/simple/job_detail/<int:job_id>', methods=['GET'])
def simpleRpmAppGetDetail(job_id):

    job = db.get_or_404(AppJob, job_id)
    return render_template("simpleRpmJobDetail.html", job=job)


@app_blueprint.route('/simple/job_detail/<int:job_id>/plots', methods=['GET'])
def simpleRpmAppGetDetailPlots(job_id):
    job = db.get_or_404(AppJob, job_id)    
    return render_template("simpleRpmJobDetailPlot.html", job=job)


@app_blueprint.route('/simple/job_detail/<int:job_id>/log', methods=['GET'])
def simpleRpmAppGetDetailLogs(job_id):
    job = db.get_or_404(AppJob, job_id)    
    return render_template("simpleRpmJobDetailLogs.html", job=job)


@app_blueprint.route('/simple/get_data/<int:job_id>>', methods=['GET'])
def simpleRpmAppGetData(job_id):
    import pandas as pd

    job = db.get_or_404(AppJob, job_id)
    
    casePath = os.path.join(output_dir, str(job.id))

    bodyfn = os.path.join(casePath, "out/Stats/MovingBody_Moving Body.txt")
    if os.path.isfile(bodyfn):
        data = pd.read_csv(bodyfn, sep='\t', usecols=["Time [s]", "Power Number [-]"])

        return {
            "MovingBody": data.to_dict(orient="records")
        }
    
    return {}

def tail(f, lines=20):
    total_lines_wanted = lines

    BLOCK_SIZE = 1024
    f.seek(0, 2)
    block_end_byte = f.tell()
    lines_to_go = total_lines_wanted
    block_number = -1
    blocks = []
    while lines_to_go > 0 and block_end_byte > 0:
        if (block_end_byte - BLOCK_SIZE > 0):
            f.seek(block_number*BLOCK_SIZE, 2)
            blocks.append(f.read(BLOCK_SIZE))
        else:
            f.seek(0,0)
            blocks.append(f.read(block_end_byte))
        lines_found = blocks[-1].count(b'\n')
        lines_to_go -= lines_found
        block_end_byte -= BLOCK_SIZE
        block_number -= 1
    all_read_text = b''.join(reversed(blocks))
    return b'\n'.join(all_read_text.splitlines()[-total_lines_wanted:])

@app_blueprint.route('/simple/get_stdout/<int:job_id>>', methods=['GET'])
def simpleRpmAppGetStdLog(job_id):
    logFn = os.path.join(output_dir, str(job_id), "log-stdout.txt")
    if os.path.isfile(logFn):
        with open(logFn, 'rb') as f:
            return tail(f, 40)
    return ""

@app_blueprint.route('/simple/get_stderr/<int:job_id>>', methods=['GET'])
def simpleRpmAppGetErrLog(job_id):
    logFn = os.path.join(output_dir, str(job_id), "log-stderr.txt")
    if os.path.isfile(logFn):
        with open(logFn, 'rb') as f:
            return tail(f, 40)
    return ""

@app_blueprint.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404