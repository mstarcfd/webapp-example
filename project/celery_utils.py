


def make_celery(app):
    from celery import current_app as current_celery_app
    celery = current_celery_app
    celery.config_from_object(app.config, namespace="CELERY")

    return celery

def make_celery2(app):
    print(app.config)
    from celery import Celery
    celery = Celery(app.import_name)
    celery.config_from_object(app.config, namespace="CELERY")        

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    return celery