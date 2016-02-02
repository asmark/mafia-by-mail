from . import app
from . import celery


services = app.make_services(app.read_config())
