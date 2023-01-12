

import enum
from project import db
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

## App database models

class JobStatus(enum.Enum):
    Unknown = 1
    Pending = 2
    Running = 3    
    Completed = 5

class AppJob(db.Model):

    __tablename__ = "appjobs"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    app_name = db.Column(db.String(128))
    job_status = db.Column(db.Enum(JobStatus), default=JobStatus.Unknown)
    created = db.Column(db.DateTime, default=datetime.now)
    completed = db.Column(db.DateTime, default=datetime.now)


## App definitions

class SimpleRpmAppDef(BaseModel):

    msb_file_name: Optional[str] = ""
    rpm: float = 60.0