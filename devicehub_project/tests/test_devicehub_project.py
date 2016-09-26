import copy
import json
import os
from unittest.mock import MagicMock
from urllib.request import Request

import requests
import validators
from assertpy import assert_that
from devicehub_project import DeviceHubProject, ProjectSettings
from devicehub_project.resources.th_submitter.th_submitter import ThAuth
from ereuse_devicehub.tests.test_resources.test_events import TestEvent
from ereuse_devicehub.tests.test_resources.test_submitter.test_submitter import TestSubmitter
from flask import request


class TestDeviceHubProject(TestEvent):
    PROJECTS = 'projects'

    def setUp(self, settings_file=None, url_converters=None):
        super().setUp(settings_file, url_converters)
        self.app.config['DEVICEHUB_PROJECT'] = {
            'TH_DOMAIN': 'https://www.reutilitza.cat',
            'TH_ACCOUNT': {
                'username': 'trial@trial.com',
                'password': 'trial'
            },
            'DEBUG': True
        }
        self.devicehub_project = DeviceHubProject(self.app)

    def set_settings(self, settings):
        # settings.RESOURCES_CHANGING_NUMBER.append(self.PROJECTS)
        super().set_settings(settings)
        settings.DOMAIN['projects'] = ProjectSettings
        settings.GRD = False

    def test_init(self):
        assert_that(self.domain).contains('projects')
        assert_that(self.domain['devices_allocate']['schema']).contains('project')
        assert_that(self.domain).contains('projects_accept', 'projects_cancel', 'projects_finish', 'projects_reject')

    def test_auth(self):
        request = Request('http://example.com')
        auth = ThAuth('username', 'password', 'domain')

        class Token:
            text = 'XYZ'
        token = Token()

        _get = requests.get
        requests.get = MagicMock(return_value=token)
        auth(request)
        requests.get.assert_called_once_with('domain/rest/session/token')
        requests.get = _get
        assert_that(request.headers['X-CSRF-Token']).is_equal_to(token.text)

    def mock_post(self, final_resource, final_url):
        def _mock_post(resource: dict, url: str):
            self.assertDictContainsSubset(final_resource, resource)  # todo sameAs

        return _mock_post

    def test_project(self):
        # Preparations: we mock the submitters to intercept and assert resources instead of sending it to TransferHub
        caller = self.app.th_submitter_caller
        caller.submit = MagicMock()
        test_client = self.app.test_client()

        # We create a TransferHub account. This account will be used to authenticate with DeviceHub
        actual_directory = os.path.dirname(os.path.realpath(__file__))
        th_account = self.get_fixture('user', 'transferhub', directory=actual_directory)
        db = th_account['databases'][0]
        self.post_and_check(self.ACCOUNTS, th_account)  # todo the token obtained is not base64 -> invalid

        login_account = {
            'email': th_account['email'],
            'password': th_account['password']
        }
        response = test_client.post('login', data=json.dumps(login_account), content_type='application/json')
        # We perform login to get the token

        token = json.loads(response.data.decode())['token']
        http_authorization = request.headers.environ['HTTP_AUTHORIZATION'] if token is None else 'Basic ' + token

        # Using the TransferHub account, we create a receiver account
        receiver = self.get_fixture('user', 'receiver', directory=actual_directory)
        environ_base = {'HTTP_AUTHORIZATION': http_authorization}
        response = test_client.post(self.ACCOUNTS, data=json.dumps(receiver), content_type='application/json',
                                    environ_base=environ_base)
        self.assert201(response._status_code)
        expected_receiver = self.get_fixture('user', 'expected_receiver', directory=actual_directory)
        receiver_from_response = json.loads(response.data.decode())
        self.assertDictContainsSubset(expected_receiver, receiver_from_response)
        # If we try to re-create the same account with the same 'url' field, it should fail
        response = test_client.post(self.ACCOUNTS, data=json.dumps(receiver), content_type='application/json',
                                    environ_base=environ_base)
        self.assert422(response._status_code)

        # Now we create a project through the TransferHub account, stating that byUser is Receiver
        original_project = self.get_fixture('project', 'project', directory=actual_directory)
        response = test_client.post('{}/{}'.format(db, self.PROJECTS), data=json.dumps(original_project),
                                    content_type='application/json', environ_base=environ_base)
        self.assert201(response._status_code)
        project_from_response = json.loads(response.data.decode())
        project = copy.deepcopy(original_project)
        project['byUser'] = project_from_response['byUser']
        project['sameAs'] = project['url']
        del project['url']
        self.assertDictContainsSubset(project, project_from_response)
        # Let's ensure the creator of the project is set to be the receiver
        assert_that(project_from_response['byUser']).is_equal_to(receiver_from_response['_id'])
        # We should not be able to create the same project again,
        # as url (internally transformed to sameAs) has to be unique
        response = test_client.post('{}/{}'.format(db, self.PROJECTS), data=json.dumps(original_project),
                                    content_type='application/json', environ_base=environ_base)
        self.assert422(response._status_code)

        # Let's create a manager, who is going to accept the project
        manager = self.get_fixture('user', 'manager', directory=actual_directory)
        response = test_client.post(self.ACCOUNTS, data=json.dumps(manager),
                                    content_type='application/json', environ_base=environ_base)
        self.assert201(response._status_code)

        # The manager accepts the project
        projects_accept = self.get_fixture('event', 'projects_accept', directory=actual_directory)
        response = test_client.post('{}/{}'.format(db, 'events/projects/accept'), data=json.dumps(projects_accept),
                                    content_type='application/json', environ_base=environ_base)
        self.assert201(response._status_code)
        accept_from_response = json.loads(
            test_client.get('{}/{}/{}'.format(db, 'events', json.loads(response.data.decode())['_id']),
                            environ_base=environ_base).data.decode())
        # We get the full response through GET
        projects_accept_expected = self.get_fixture('event', 'projects_accept_expected', directory=actual_directory)
        # Project and byUser shouldn't be an URL, as we are not sending the result through the Submitter
        assert_that(validators.url(accept_from_response['project'])).is_false()
        assert_that(validators.url(accept_from_response['byUser'])).is_false()
        self.assertDictContainsSubset(projects_accept_expected, accept_from_response)

        # We assign some devices to the project
        devices_allocate = self.get_fixture('event', 'devices_allocate', directory=actual_directory)
        # This is done from a manager directly from a DeviceHub, so identifiers are internals, not url
        devices_allocate['project'] = project_from_response['_id']  # We allocate to the receiver
        # Note that we do not need to assign 'to', as we infer this information from the project's byUser field
        devices_allocate['devices'] = self.devices_id  # Some devices to allocate
        # We use ThSubmitter to send it to TransferHub. We are going to mock the Submitter
        devices_allocate_expected = self.get_fixture('event', 'devices_allocate_expected', directory=actual_directory)
        devices_allocate_expected['to'] = receiver_from_response['sameAs']
        mock_post = self.mock_post(devices_allocate_expected, 'http://www.reutilitza.cat/events/devices/')
        caller.submit.side_effect = TestSubmitter.mock_submit(caller.submitter, caller.token, caller.app, mock_post)
        # It can be done by another manager, like the admin user used in regular tests
        self.post_and_check('events/devices/allocate', devices_allocate)
        assert_that(caller.submit.call_count).is_equal_to(1)  # We only submit one event to TransferHub
        # If we try to allocate again, DeviceHub sees that the devices were already allocated to the user
        _, status_code = self.post('events/devices/allocate', devices_allocate)
        self.assert422(status_code)
