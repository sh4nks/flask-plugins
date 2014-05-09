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
    └── __init__.py


A more complex plugin could look like this:

.. sourcecode:: text

    my_plugin
    ├── __init__.py
    ├── views.py
    ├── models.py
    ├── forms.py
    ├── static
    │   └── style.css
    └── templates
        └── myplugin.html


To add the extension to your application you simply can do this::

    from flask.ext.plugins import PluginManager

    plugin_manager = PluginManager(app)

    plugin_manager.setup_plugins()

or if you are using the factory pattern::

    from flask.ext.plugins import PluginManager

    plugin_manager = PluginManager()
    plugin_manager.init_app(app)

    plugin_manager.setup_plugins()


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


Hooks
-----

We also provide a simply hook system. It allows you to extend your existing
code without modifying it. To get started you need to initialize the
``HookManager``::

    from flask.ext.plugins import HookManager, Hook()

    hooks = HookManager()

now you can create a new ``Hook`` which can than be used by your plugins::

    # creating a hello_world hook
    hooks.new("hello_world")

and finally you can add a callback to your newly created hook::

    def print_hello():
        return "Hello World"

    hooks.add("hello_world", print_hello)

To run your hooks, you simply need to add on specific places this::

    hooks.run_hook("hello_world")

and if you also want to use the hooks in your template, you have to update
jinja's global context and then you should be able to run the hooks::

    app.jinja_env.globals.update(hooks=hooks)

In the template you need to use the ``run_template_hook`` method::

    {{ hooks.run_template_hook("some_template_hook") | safe }}



If you want to see a fully working example, please check it out
`here <https://github.com/sh4nks/flask-plugins/tree/master/example>`_.


The Plugin Class
================

Every ``Plugin`` should implement this class. It is used to get plugin specific
data (later, I want to use for the metadata a ``.json`` file or something like
this) and to call the methods which are stated below.

.. autoclass:: Plugin

  .. autoattribute:: name

  .. autoattribute:: description

  .. autoattribute:: author

  .. autoattribute:: license

  .. autoattribute:: version

  .. automethod:: setup

  .. automethod:: enable

  .. automethod:: disable

  .. automethod:: install

  .. automethod:: uninstall


HelloWorld Plugin
-----------------

For a fully working example check out the example app
`here <https://github.com/sh4nks/flask-plugins/tree/master/example>`_.

A HelloWorld Plugin could look like this::

    class HelloWorld(Plugin):
        name = "Hello World Plugin"
        description = "Flashes Hello World"
        author = "John Doe"
        license = "BSD"
        version = "1.3.1"

        def setup(self):
            register_blueprint_here()

        def enable(self):
            # add a callback to the index hook
            hooks.add("index", flash_hello_world)

        def disable(self):
            # remove the previously added callback from the index hook
            hooks.remove("index", flash_hello_world)

        def install(self):
            # there is nothing to install
            pass

        def uninstall(self):
            # ... and nothing to uninstall
            pass


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


Hook System
-----------

.. autoclass:: Hook
  :members:
  :special-members:
  :exclude-members: __weakref__

.. autoclass:: HookManager
  :members:
  :special-members:
  :exclude-members: __weakref__
