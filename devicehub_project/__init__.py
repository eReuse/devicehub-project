# We import LiveSettings so it gets loaded by Python, and automatically added to our domain
# Remember, this only happens when the app is loading. After this, you have to manually add the resource
from ereuse_devicehub.default_settings import RESOURCES_CHANGING_NUMBER
RESOURCES_CHANGING_NUMBER.add('project')  # todo this shouldn't be done this way

from devicehub_project.resources.event import project
from devicehub_project.resources.project.settings import ProjectSettings

from devicehub_project.devicehub_project import DeviceHubProject