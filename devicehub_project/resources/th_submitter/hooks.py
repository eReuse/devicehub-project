from ereuse_devicehub.resources.account.domain import AccountDomain
from ereuse_devicehub.resources.event.device import DeviceEventDomain
from ereuse_devicehub.utils import Naming
from flask import current_app

def send_project_events_to_transferhub(resource: str, events: list):
    names = {Naming.resource(DeviceEventDomain.new_type(event_name)) for event_name in ('Allocate', 'Receive')}
    if resource in current_app.config.setdefault('DEVICEHUB_PROJECT_SUBMITTER_EVENTS', names):
        for event in events:
            current_app.th_submitter_caller.submit(str(event['_id']), AccountDomain.get_requested_database(), resource)
