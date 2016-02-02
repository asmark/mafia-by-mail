import celery

from . import app as mbm_app

config = mbm_app.read_config()
app = celery.Celery('mbm', broker=config['celery']['broker'],
                    include=['mbm.tasks'])
