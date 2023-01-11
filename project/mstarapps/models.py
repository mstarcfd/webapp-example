

import enum
from project import db
from datetime import datetime

class JobStatus(enum.Enum):
    Unknown = 1
    Pending = 2
    Running = 3    
    Completed = 5


class AppJob(db.Model):

    __tablename__ = "appjobs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.String(128))
    slurm_job_id = db.Column(db.String(128), default="")
    job_status = db.Column(db.Enum(JobStatus), default=JobStatus.Unknown)
    created = db.Column(db.DateTime, default=datetime.now)
    completed = db.Column(db.DateTime, default=datetime.now)


