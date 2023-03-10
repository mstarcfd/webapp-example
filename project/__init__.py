import os

from flask import Flask
from flask_celeryext import FlaskCeleryExt
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect  # new

from project.config import config  
from project.celery_utils import make_celery2

# instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()
ext_celery = FlaskCeleryExt(create_celery_app=make_celery2) 
csrf = CSRFProtect()  # new

suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def human_bytes(nbytes):
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])

def create_app(config_name=None):  # updated    
    if config_name is None:
        config_name = os.environ.get("FLASK_CONFIG", "development")

    # instantiate the app
    app = Flask(__name__)
    
    # set config
    app.config.from_object(config[config_name])

    # set up extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ext_celery.init_app(app)
    csrf.init_app(app)

    # register blueprints
    from project.users import users_blueprint
    from project.mstarapps import app_blueprint

    app.register_blueprint(users_blueprint)
    app.register_blueprint(app_blueprint)

    # template filters
    app.jinja_env.filters["human_bytes"] = human_bytes
    

    # shell context for flask cli
    @app.shell_context_processor
    def ctx():
        return {"app": app, "db": db}

    return app