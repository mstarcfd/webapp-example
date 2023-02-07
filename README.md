

# Overview

This is an example web application that performs a complete computational fluid dynamics (CFD) analysis using M-Star CFD. The example uses the built-in agitated vessel as a starting point, and allows the user to change a few specific inputs on a web form.

The app will then apply the changes to the M-Star CFD model, run it in the Solver, and post-process the results into images, movies, and a PDF report. 

# Architecture

This web app example uses Python Flask, Celery, Redis or Rabbitmq, and other libraries to implement the web application. Some client side javascript is present to plot data of running cases.

The backend Celery tasks use 2 different queues: one for general purpose tasks such as pre-processing or exporting files, and one for GPU-specific tasks. This lets us isolate the GPU work into a separate task queue which will have real harware resource constraints. 

The front-end:

- uikit
- d3 Observable Plot

# Environment

Install to system:

- ffmpeg
- python 3.9 or 3.10
- gtk 3.0
- NVidia driver
- Open MPI 3.1+ 

Setup Redis or Rabbitmq

Initialize a virtual environment and install the base environment. 

```
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

To install the M-Star Pre-processing Library, you will need to download and extract one of the M-Star CFD packages from the download site. Then modify your python environment using one of the methods documented here -- https://docs.mstarcfd.com/12_MStar_API/txt-files/installation.html . 

Now add the M-Star Solver to your PATH by sourcing the `/path/to/mstarXYZ/mstar.sh` file which is included in the above package you downloaded. 

Setup your M-Star license using your preferred method. 

You can use the below script to initialize the environment. Modify for your needs

```
# Python: flask, celery, mstarpypost, etc
source venv/bin/activate

# Add M-Star CFD
MSTAR_INSTALL=/path/to/mstarXYZ
source $MSTAR_INSTALL/mstar.sh

# Add M-Star CFD Python module to environment
# Alternatively, you can add `mstar.pth` file to the virtual environment sitepackages dir
export PYTHONPATH=$MSTAR_INSTALL/lib

# Setup M-Star license
export mstar_LICENSE=5053@mycompany.rlm.server.net
```


# Start-up (development environment)

Start Redis

`docker run -p 6379:6379 --name some-redis -d redis`

Start web worker

`flask run`

Start general purpose backend worker. This worker will perform pre-processing, export, and other work.

`celery -A app.celery worker`

Start GPU backend worker with a concurrency of **1** which will limit one GPU job at a time. Multiple GPUs and resource aware queuing is not implemented. 

`celery -A app.celery worker -Q gpu -c 1`



# Development guide

Each "M-Star App" will usually require the following customizations:

- M-Star CFD .msb file with the base line inputs
- What can the user change?
    - Web form front-end (`project/mstarapps/templates`)
    - Web form back-end (`project/mstarapps/forms.py`)
    - Celery task to apply web-form inputs to model changes (`project/mstarapps/tasks.py`)
- What result does the user see?
    - Celery task to perform post-processing (`project/mstarapps/tasks.py`)
    - Customizations to *Plots* page on the job status (`project/mstarapps/templates`)
- URL routing (`project/mstarapps/views.py`)


# Future work/ideas


Pre-processing
- Display 3D pre-processor state
- Run parameter sweep from an app and display comparative analysis

Post-Processing
- Email PDF report to users
- Put simulation results into database

UI
- More control over running jobs
- Move some potentially heavier web work to celery tasks (eg. stat file reading)
- Example showing two jobs from same app being compared
- Live updating logs/plots using web sockets
- Some way to delete/archive old results

Integration
- Authentication
- SLURM integration
- Docker compose support

Data exploration
- Display results in 3D in web using vtk.js or Trame
- Stat file data explorer 