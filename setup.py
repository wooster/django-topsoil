#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages

import os

setup(
    name = 'django-topsoil',
    version = '0.1',
    url = 'https://github.com/wooster/django-topsoil',
    download_url = 'https://github.com/wooster/topsoil/downloads',
    license = 'BSD',
    description = "topsoil is a Django framework for creating APIs.",
    author = 'Andrew Wooster',
    author_email = 'andrew@planetaryscale.com',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
    install_requires = [
        'django-oauth',
    ],
)
