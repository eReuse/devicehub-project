from devicehub_project.resources.event.project.hooks import get_to_account_from_project
from ereuse_devicehub.resources.submitter.submitter_caller import SubmitterCaller

from devicehub_project.resources.th_submitter.hooks import send_project_events_to_transferhub
from devicehub_project.resources.th_submitter.th_submitter import ThSubmitter


class DeviceHubProject:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.on_inserted += send_project_events_to_transferhub
        app.on_insert_devices_allocate.targets.insert(0, get_to_account_from_project)
        app.th_submitter_caller = SubmitterCaller(app, ThSubmitter)
