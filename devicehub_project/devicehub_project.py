from ereuse_devicehub.resources.submitter.submitter_caller import SubmitterCaller

from devicehub_project.resources.project.settings import Project
from devicehub_project.resources.th_submitter.hooks import send_project_events_to_transferhub
from devicehub_project.resources.th_submitter.th_submitter import ThSubmitter


class DeviceHubProject:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.on_inserted += send_project_events_to_transferhub
        app.th_submitter_caller = SubmitterCaller(app, ThSubmitter)
