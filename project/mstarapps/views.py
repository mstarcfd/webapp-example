
from .forms import SimpleRpmForm
from flask import request, flash, redirect, url_for, render_template
from . import app_blueprint
from .models import AppJob
from project import db
from sqlalchemy import desc

@app_blueprint.route('/simple', methods=['GET', 'POST'])
def simpleRpmForm():
    form = SimpleRpmForm()
    if form.validate_on_submit():
        flash("Thanks for submitting your case")
        return redirect(url_for("mstarapp.dashboard"))
    return render_template("simpleRpmForm.html", form=form)

@app_blueprint.route('/manage_jobs', methods=['GET'])
def manage_jobs():
    appJobs = db.session.execute(db.select(AppJob).order_by(AppJob.created.desc())).scalars()

    return render_template("manage_jobs.html", jobs=appJobs)

@app_blueprint.route('/', methods=['GET'])
def dashboard():
    return render_template("dashboard.html")

