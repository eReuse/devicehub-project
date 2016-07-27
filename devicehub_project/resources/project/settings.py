from ereuse_devicehub.resources.device.schema import Device
from ereuse_devicehub.resources.place.settings import Place
from ereuse_devicehub.resources.resource import ResourceSettings
from ereuse_devicehub.resources.schema import Thing
from ereuse_devicehub.validation.coercer import Coercer


class Project(Thing):
    tags = {
        'type': 'list',
        'valueschema': {
            'type': 'string'
        }
    }
    shortDescription = {
        'type': 'string',
        'description': 'A brief description of 140 characters, in a Twitter-style, '
                       'transmitting the main idea of the project.',
        'maxlength': 150
    }
    image = {
        'type': 'url',
        'description': 'A representative image of the project.'
    }
    deadline = {
        'type': 'datetime',
        'description': 'Date where the devices should arrive before'
    }
    requiredDevices = {
        'type': 'dict',
        'valueschema': {
            'type': 'natural'
        },
        'propertyschema': {
            'type': 'string',
#            'allowed': [Device.types | {'DesktopWithPeripherals'}]
            # todo allowed values
        }
    }
    address = Place.address
    links = {
        'type': 'dict',
        'valueschema': {
            'type': 'url'
        },
        'propertyschema': {
            'type': 'string',
            'allowed': ('website', 'facebook', 'twitter'),
        }
    }
    votes = {
        'type': 'natural'
    }
    byUser = {
        'type': 'objectid',
        'data_relation': {
            'resource': 'accounts',
            'field': '_id',
            'embeddable': True
        },
        'sink': 2,
        'coerce_with_context': Coercer.url_to_id
    }


class ProjectSettings(ResourceSettings):
    resource_methods = ['GET', 'POST']
    item_methods = ['GET', 'PATCH', 'DELETE', 'PUT']
    _schema = Project
    datasource = {
        'default_sort': [('_created', -1)],
        'source': 'projects'
    }
    extra_response_fields = ResourceSettings.extra_response_fields + ['tags', 'shortDescription', 'image', 'deadline',
                                                                      'requiredDevices', 'address', 'links', 'votes',
                                                                      'byUser']
