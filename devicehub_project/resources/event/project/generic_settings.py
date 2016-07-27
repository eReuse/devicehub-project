from ereuse_devicehub.resources.event.settings import Event
from ereuse_devicehub.resources.resource import Resource

from devicehub_project.resources.event.project.domain import ProjectEventDomain
from devicehub_project.resources.event.project.settings import ProjectEvent, ProjectEventSubSettings, prefix

"""
    Registers the generic types for the events.
"""

for generic_type in ProjectEventDomain.GENERIC_TYPES:
    resource_settings = {
        '_settings': dict(Event._settings, **prefix)
    }
    Resource.create(generic_type, ProjectEvent, {}, ProjectEventSubSettings, resource_settings)
