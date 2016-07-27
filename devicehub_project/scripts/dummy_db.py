from ereuse_devicehub.scripts.dummy_db import DummyDB


class DeviceHubProjectDummyDB(DummyDB):
    example_th_account = {
            "email": "transferhub@ereuse.org",
            "active": True,
            "isOrganization": False,
            "password": "random",
            "role": "admin",
            "@type": "Account",
            "databases": ["db1"]
        }
    """
        Simple class to create a database from 0, adding a dummy user and some devices. Ready to test!

        To use it do the following in your app.py::

            app = DeviceHub()
            d = DummyDB(app)
            d.create_dummy_devices()

        This method uses the test class of TestSnapshot, and the credentials in
        :func:`ereuse_devicehub.tests.TestBase.create_dummy_user`.

    """

    def __init__(self, app):
        super().__init__(app)
        self.test_snapshot.post_and_check(self.test_snapshot.ACCOUNTS, self.example_th_account)
