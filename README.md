[![Build Status](https://github.com/sh4nks/flask-plugins/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/sh4nks/flask-plugins/actions/workflows/ci.yml)

# Flask-Plugins

Flask-Plugins provides an easy way to create plugins for your
application. It is also possible to create Events which can than be used to
extend your application without the need to modify your core code.


# Installation

First you need to install it. It is available on the [Python Package Index](https://pypi.python.org/pypi/flask-plugins).

    pip install flask-plugins

and then you need to initialize it somewhere in your code.

    from flask_plugins import PluginManager

    plugin_manager = PluginManager()

it also supports the factory pattern.

    from flask_plugins import PluginManager

    plugin_manager = PluginManager()
    plugin_manager.init_app(app)


# Documentation

The documentation is located [here](https://flask-plugins.readthedocs.org/en/latest/).


# License

[BSD License](./LICENSE)
