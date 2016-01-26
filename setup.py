"""
Flask-Plugins
-------------

Flask-Plugins makes it possible, to create plugins for your
application. In addition to the plugin system, it also provides a simple
event system which can be used by plugins to extend your application without
the need to modify your core code.


And Easy to Setup
`````````````````

First of all, you have to install it:

.. code:: bash

    $ pip install flask-plugins

and then you need to initialize it somewhere in your code.

.. code:: python

    from flask_plugins import PluginManager

    plugin_manager = PluginManager(app)

Want to use the factory pattern? No problem!

.. code:: python

    from flask_plugins import PluginManager

    plugin_manager = PluginManager()
    plugin_manager.init_app(app)

Resources
`````````

* `source <https://github.com/sh4nks/flask-plugins>`_
* `docs <https://flask-plugins.readthedocs.org/en/latest>`_
* `issues <https://github.com/sh4nks/flask-plugins/issues>`_

"""
from setuptools import setup
import re
import ast


def _get_version():
    version_re = re.compile(r'__version__\s+=\s+(.*)')

    with open('flask_plugins/__init__.py', 'rb') as fh:
        version = ast.literal_eval(
            version_re.search(fh.read().decode('utf-8')).group(1))

    return str(version)


setup(
    name='Flask-Plugins',
    version=_get_version(),
    url='https://github.com/sh4nks/flask-plugins',
    license='BSD',
    author='Peter Justin',
    author_email='peter.justin@outlook.com',
    description='Create plugins for your Flask application',
    long_description=__doc__,
    packages=['flask_plugins'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.6',
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose>=1.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4'
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
