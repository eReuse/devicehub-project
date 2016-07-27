from ereuse_devicehub.resources.event.device.allocate.settings import Allocate
from ereuse_devicehub.resources.event.device.receive.settings import Receive
from ereuse_devicehub.resources.event.settings import Event, EventSettings

prefix = {'prefix': 'projects'}


class ProjectEvent(Event):
    pass


ProjectEvent._settings = dict(ProjectEvent._settings, **{'url': 'projects'}, **prefix)  # todo make this nice

# Adds a project field to Allocate and Receive
Allocate.project = Receive.project = {
    'type': 'string',
    'data_relation': {
        'resource': 'projects',
        'field': '_id',
        'embeddable': True
    },
}


class ProjectEventSettings(EventSettings):
    _schema = ProjectEvent


class ProjectEventSubSettings(ProjectEventSettings):
    _schema = False
    resource_methods = ['POST']
    item_methods = []
