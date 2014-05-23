"""
Flask-Plugins
-------------

Flask-Plugins provides an easy way to create plugins for your
application. It is also possible to create Events which can than be used to
extend your application without the need to modify your core code.


And Easy to Setup
`````````````````

First you need to install it via:

.. code:: bash

    $ pip install flask-plugins

and then you need to initialize it somewhere in your code.

.. code:: python

    from flask.ext.plugins import PluginManager

    plugin_manager = PluginManager(app)

It also supports the factory pattern for creating your app.

.. code:: python

    from flask.ext.plugins import PluginManager

    plugin_manager = PluginManager()
    plugin_manager.init_app(app)

Resources
`````````

* `source <https://github.com/sh4nks/flask-plugins>`_
* `docs <https://flask-plugins.readthedocs.org/en/latest>`_
* `issues <https://github.com/sh4nks/flask-plugins/issues>`_

"""
from setuptools import setup

setup(
    name='Flask-Plugins',
    version='1.1',
    url='http://github.com/sh4nks/flask-plugins/',
    license='BSD',
    author='sh4nks',
    author_email='sh4nks7@gmail.com',
    description=
        'A Extension that makes it possible to create plugins in Flask.',
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
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
