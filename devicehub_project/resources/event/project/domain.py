from ereuse_devicehub.resources.event.domain import EventDomain
from ereuse_devicehub.utils import Naming


class ProjectEventDomain(EventDomain):
    GENERIC_TYPES = {'Accept', 'Reject', 'Finish', 'Cancel'}

    @staticmethod
    def add_prefix(type_name: str) -> str:
        """
        Adds a prefix to the type of a DeviceEvent (or subclass), if needed, and returns the full type with the prefix.

        It is used as coerce in @type field of DeviceEvent.
        """
        from devicehub_project.resources.event.project.settings import ProjectEvent
        if type_name in (subclass.__name__ for subclass in ProjectEvent.subclasses()):
            return ProjectEventDomain.new_type(type_name)
        else:
            return str(type_name)

    @staticmethod
    def new_type(type_name):
        from devicehub_project.resources.event.project.settings import ProjectEvent
        return Naming.new_type(type_name, ProjectEvent._settings['prefix'])