import json
import os
from unittest.mock import MagicMock

from assertpy import assert_that
from ereuse_devicehub.tests.test_resources.test_events import TestEvent
from ereuse_devicehub.tests.test_resources.test_submitter.test_submitter import TestSubmitter
from flask import request

from devicehub_project import DeviceHubProject, ProjectSettings


class TestDeviceHubProject(TestEvent):
    PROJECTS = 'projects'

    def setUp(self, settings_file=None, url_converters=None):
        super().setUp(settings_file, url_converters)
        self.app.config['DEVICEHUB_PROJECT'] = {
            'TH_DOMAIN': 'https://www.reutilitza.cat',
            'TH_ACCOUNT': {
                'username': '',
                'password': ''
            }
        }
        self.devicehub_project = DeviceHubProject(self.app)
        self.app.config['GRD'] = False

    def set_settings(self, settings):
        settings.DOMAIN['projects'] = ProjectSettings
       # settings.RESOURCES_CHANGING_NUMBER.append(self.PROJECTS)
        super().set_settings(settings)

    def test_init(self):
        assert_that(self.domain).contains('projects')
        assert_that(self.domain['devices_allocate']['schema']).contains('project')
        assert_that(self.domain).contains('projects_accept', 'projects_cancel', 'projects_finish', 'projects_reject')

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

        # Now we create a project through the TransferHub account, stating that byUser is Receiver
        project = self.get_fixture('project', 'project', directory=actual_directory)
        response = test_client.post('{}/{}'.format(db, self.PROJECTS), data=json.dumps(project), content_type='application/json',
                                    environ_base=environ_base)
        self.assert201(response._status_code)
        project_from_response = json.loads(response.data.decode())
        project['byUser'] = project_from_response['byUser']
        project['sameAs'] = project['url']
        del project['url']
        self.assertDictContainsSubset(project, project_from_response)  # todo sameAs
        assert_that(project_from_response['byUser']).is_equal_to(response['_id'])

        # We accept the project
        projects_accept = self.get_fixture('event', 'projects_input', directory=actual_directory)
        # Accept is done in DeviceHub by an admin user, so we need to intercept the TransferHub submitter
        # to not to send actual info to a TransferHub, but to assert it
        projects_accept_expected = self.get_fixture('event', 'projects_output', directory=actual_directory)
        mock_post = self.mock_post(projects_accept_expected,
                                   'http://www.reutilitza.cat/events/projects/')  # todo url id project
        # The actual call
        caller.submit.side_effect = TestSubmitter.mock_submit(caller.submitter, caller.token, caller.app, mock_post)
        # This is done by an admin user through DeviceHub; we use the default user for tests
        self.post_and_check('events/projects/accept', projects_accept)
        assert_that(caller.submit.call_count).is_equal_to(1)

        # We assign some devices to the project
        devices_accept = self.get_fixture('event', 'devices_accept', directory=actual_directory)
        # This is done again by the admin user
        devices_accept_expected = self.get_fixture('event', 'devices_accept_final', directory=actual_directory)
        mock_post = self.mock_post(devices_accept_expected,
                                   'http://www.reutilitza.cat/events/devices/')  # todo url id project
        caller.submit.side_effect = TestSubmitter.mock_submit(caller.submitter, caller.token, caller.app, mock_post)
        # The actual call
        self.post_and_check('events/devices/accept', devices_accept)
        assert_that(caller.submit.call_count).is_equal_to(1)
