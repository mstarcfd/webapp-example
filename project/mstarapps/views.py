
from .forms import SimpleRpmForm
from flask import request, flash, redirect, url_for, render_template
from . import app_blueprint

@app_blueprint.route('/simple', methods=['GET', 'POST'])
def simpleRpmForm():
    form = SimpleRpmForm()
    if form.validate_on_submit():
        flash("Thanks for submitting your case")
        return redirect(url_for("mstarapp.dashboard"))
    return render_template("simpleRpmForm.html", form=form)

@app_blueprint.route('/', methods=['GET'])
def dashboard():
    return render_template("dashboard.html")

