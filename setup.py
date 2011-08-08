#!/usr/bin/python

import os
from setuptools import setup, find_packages

from django_boolean_mixins import VERSION


MODULE_NAME = 'django-boolean-mixins'
PACKAGE_DATA = list()

for directory in [ 'templates', 'static' ]:
    for root, dirs, files in os.walk( os.path.join( MODULE_NAME, directory )):
        for filename in files:
            PACKAGE_DATA.append("%s/%s" % ( root[len(MODULE_NAME)+1:], filename ))


def read( fname ):
    try:
        return open( os.path.join( os.path.dirname( __file__ ), fname ) ).read()
    except IOError:
        return ''


META_DATA = dict(
    name = "django-boolean-mixins",
    version = ".".join(map(str, VERSION)),
    description = read('DESCRIPTION'),
    long_description = read('README.markdown'),
    license='GNU LGPL',

    url = "https://github.com/chibisov/django_boolean_mixins",

    packages = find_packages(),
    package_data = { '': PACKAGE_DATA, },

    install_requires = [ 'django>=1.2', ],
)

if __name__ == "__main__":
    setup( **META_DATA )

