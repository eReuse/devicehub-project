from ereuse_devicehub.resources.event.device.allocate.settings import Allocate
from ereuse_devicehub.resources.event.device.receive.settings import Receive
from ereuse_devicehub.resources.event.settings import Event, EventSettings
from ereuse_devicehub.validation.coercer import Coercer

prefix = {'prefix': 'projects'}


class ProjectEvent(Event):
    project = {
        'type': 'objectid',
        'data_relation': {
            'resource': 'projects',
            'field': '_id',
            'embeddable': True
        },
        'coerce_with_context': Coercer.url_to_id,
}


settings = ProjectEvent._settings.copy()
settings.update({'url': 'projects'})
settings.update(prefix)
ProjectEvent._settings = settings  # todo make this nice

# Adds a project field to devices:Allocate and devices:Receive
Allocate.project = Receive.project = ProjectEvent.project
# We can extract the 'to' field from the byUser of the project (look at hooks.py)
Allocate.to['or'].append('project')


class ProjectEventSettings(EventSettings):
    _schema = ProjectEvent


class ProjectEventSubSettings(ProjectEventSettings):
    _schema = False
    resource_methods = ['POST']
    item_methods = []
