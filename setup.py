import sys
from setuptools import setup, find_packages

packages = find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*'])

kwargs = {
    'packages': packages,
    'include_package_data': True,
    'install_requires': [
        'django>=1.4',
    ],

    'name': 'django-registration2',
    'version': __import__('registration').get_version(),
    'author': 'Byron Ruth',
    'author_email': 'b@devel.io',
    'description': 'Registration and moderation utilites',
    'license': 'BSD',
    'keywords': 'registration moderation',
    'url': 'https://github.com/bruth/django-registration2',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
}

setup(**kwargs)
