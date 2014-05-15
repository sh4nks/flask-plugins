=============
Flask-Plugins
=============
.. currentmodule:: flask.ext.plugins

Flask-Plugins provides an easy way to create plugins and add hooks for your
application. It is also possible to create Hooks which can than be used to
extend your application without the need to modify your core code.


**I would love to have some feedback about this extension :)**

I'm currently not really satisfied with the current state of the code
but it works. When I have a little bit more time, I want to investigate how
to use a data store, to save the current status of the plugin. For example,
if the plugin is installed or uninstalled and so on..


.. contents::
   :local:
   :backlinks: none


Quickstart
==========
A plugin has it's own folder where all the plugin specific files are living
like shown in the examples below.


.. sourcecode:: text

    my_plugin
    ├── info.json
    └── __init__.py


A more complex plugin could look like this:

.. sourcecode:: text

    my_plugin
    ├── info.json                Contains the Plugin's metadata
    ├── license.txt              The full license text of your plugin
    ├── __init__.py              The plugin's main class is located here
    ├── views.py
    ├── models.py
    ├── forms.py
    ├── static
    │   └── style.css
    └── templates
        └── myplugin.html


The only way to disable a plugin without removing is, to add a ``DISABLED``
in the plugin's root folder. You need to reload your application in order to
to have the plugin fully disabled. A disabled plugin could look like this::

    my_plugin
    ├── DISABLED            # Just add a empty file named "DISABLED" to disable a plugin
    ├── info.json
    └── __init__.py


To add the extension to your application you simply can do this::

    from flask.ext.plugins import PluginManager

    plugin_manager = PluginManager(app)


or if you are using the factory pattern::

    from flask.ext.plugins import PluginManager

    plugin_manager = PluginManager()
    plugin_manager.init_app(app)


The Plugin Loader looks in the ``__init__.py`` for a ``__plugin__`` variable
which specifies the Plugin Class. If no such variable exists, the loader will
just go on to the next plugin (if any) and trying to load them. But if a wrong
plugin class is specified it will raise a exception.

So for example, the ``__plugin__`` var for a ``HelloWorld`` plugin class would
look like this::

    __plugin__ = "HelloWorld"


To get a list of all available plugins you can use either
``plugin_manager.plugins`` or ``get_plugins_list()`` which basically wraps
the ``plugin_manager.plugins`` property. To get only one specific plugin,
you can use ``get_plugin(name)``


To make use of the ``install`` and ``uninstall`` methods, you need to implement
them by yourself in your applications core because we are not bound to a
database. **TODO:** Provide a example


Events
------

We also provide a Event system out of the box. It is up to you if you want to
extend your application with events. If you decide to use it, than you
just need to add in specific places in your code the :func:`emit_event` function
with the name of your event and optionally the data which can be modified by a
plugin. After you have initilized the :class:`PluginManager` you can do this::

    from flask.ext.plugins import emit_event

    emit_event("before-data-rendered", data)

and than you can add a callback (e.q. in your plugin setup method)
to your newly created event::

    from flask.ext.plugins import connect_event

    def do_before_data_rendered(data):
        return "returning modified data"

    connect_event("before-data-rendered", do_before_data_rendered)


Of course you also do that in your templates - For this we have already added
:func:`emit_event` to your jinja env context. So you just need to call it in the
template::

    {{ emit_event("before-data-rendered") }}



If you want to see a fully working example, please check it out
`here <https://github.com/sh4nks/flask-plugins/tree/master/example>`_.


The Plugin Class
================

Every ``Plugin`` should implement this class. It is used to get plugin specific
data and the :class:`PluginManager` tries call the methods which are stated below.

.. autoclass:: Plugin

  .. automethod:: setup

  .. automethod:: install

  .. automethod:: uninstall


HelloWorld Plugin
-----------------

For a fully working example check out the example app
`here <https://github.com/sh4nks/flask-plugins/tree/master/example>`_.

A HelloWorld Plugin could look like this::

    class HelloWorld(Plugin):
        def setup(self):
            connect_event(before-data-rendered, do_before_data_rendered)

        def install(self):
            # there is nothing to install
            pass

        def uninstall(self):
            # ... and nothing to uninstall
            pass


Looks simple, eh? :)


API Documentation
=================

Plugin System
-------------

.. autoclass:: PluginManager
  :members:
  :special-members:
  :exclude-members: __weakref__


.. autofunction:: get_plugins_list

.. autofunction:: get_plugin


Event System
------------

.. autoclass:: EventManager
  :members:
  :special-members:
  :exclude-members: __weakref__


.. autofunction:: emit_event

.. autofunction:: connect_event

.. autofunction:: iter_listeners
