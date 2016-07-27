from setuptools import setup, find_packages

setup(
    name='DeviceHub-Project',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/eReuse/devicehub-project.git',
    license='AGPLv3 License',
    author='eReuse team',
    author_email='x.bustamante@ereuse.org',
    description='',
    install_requires=[
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Office/Business',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
