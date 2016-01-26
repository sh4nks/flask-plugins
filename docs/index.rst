=============
Flask-Plugins
=============
.. currentmodule:: flask_plugins

Flask-Plugins provides an easy way to create plugins for your
application. It is possible to create Events which can then be used to
extend your application without the need to modify your core code.


.. contents::
   :local:
   :backlinks: none


Quickstart
==========
First of all, you have to initialize the extension. This can be done in two
different ones.

The first one is to initalize it directly::

    from flask.ext.plugins import PluginManager

    plugin_manager = PluginManager(app)


where as the second one is to use the factory pattern::

    from flask.ext.plugins import PluginManager

    plugin_manager = PluginManager()
    plugin_manager.init_app(app)



Plugin Structure
----------------

After the first step is done, you can start developing your first plugin.
The most minimal plugin needs to have at least it's **own** directory,
a **info.json** file, where some meta data about the plugin is stored and
last but not least a **__init__.py** file where the name of the plugin class
is specified.

For example, the structure of small plugin can look like this:

.. sourcecode:: text

    my_plugin
    |-- info.json
    |-- __init__.py


the structure of a more complex plugin can also look like this:

.. sourcecode:: text

    my_plugin
    |-- info.json                Contains the Plugin's metadata
    |-- license.txt              The full license text of your plugin
    |-- __init__.py              The plugin's main class is located here
    |-- views.py
    |-- models.py
    |-- forms.py
    |-- static
    |   |-- style.css
    |-- templates
        |-- myplugin.html


Hello World!
------------

For a better understanding you can also have a look at the `example
application`_.

Another important note is, that you have to specify the name of the plugin class
in the **__init__.py** file. The reason for this is that the Plugin Loader
looks in the ``__init__.py`` for a ``__plugin__`` variable to load the plugin.
If no such variable exists, the loader will just go on to the next plugin.
and if the specified name in ``__init__.py`` doesn't match the name of the
actual plugin class it will raise an exception.

So for example, the ``__plugin__`` variable, in the ``__init__.py`` file,
for a ``HelloWorld`` plugin class could look like this::

    __plugin__ = "HelloWorld"

A HelloWorld Plugin could, for example, look like this::

    class HelloWorld(Plugin):
        def setup(self):
            connect_event('before-data-rendered', do_before_data_rendered)


In addition to this, the **info.json** file is also required. It just contains
some information about the plugin::

    {
        "identifier": "hello_world",
        "name": "Hello World",
        "author": "sh4nks",
        "license": "BSD",
        "description": "A Hello World Plugin.",
        "version": "1.0.0"
    }

For more available fields, see `The info.json File`_.


Enabling and Disabling Plugins
------------------------------

This extension, unlike other python plugin systems, uses a different approach
for handling plugins. Instead of installing plugins from PyPI, plugins should
just be dropped into a directory. Another thing that is unique, is to disable
plugins without touching any source code. To do so, a simple *DISABLED* file
in the plugin's root directory is enough. This can either be done by hand or
with the methods provided by :class:`PluginManager`.

The directory structure of a disabled plugin is shown below.

.. sourcecode:: text

    my_plugin
    |-- DISABLED            # Just add a empty file named "DISABLED" to disable a plugin
    |-- info.json
    |-- __init__.py

The server needs to be restarted in order to disable the plugin. This is a
limitation of Flask. However, it is possible, to restart the application
by sending a HUP signal to the application server. The following code snippets,
are showing how this can be done with the WSGI server *gunicorn*. Gunicorn has
be to started in daemon (``--daemon``) mode in order for this to work.

.. sourcecode:: python

    @app.route('/restart-server/')
    def restart_server():
      os.kill(os.getpid(), signal.SIGHUP)

Which you can then call via a AJAX call.

.. sourcecode:: javascript

    function reload_server() {
      // Reload Server
      $.ajax({
        url: "/reload-server/"
      });
      // Wait 1 second and reload page
      setTimeout(function(){
        window.location = document.URL;
      }, 1000);
    }

This can then be called with a simple button (given you have included the JS
file in your html template).

.. sourcecode:: html

    <button onclick='reload_server()'>Reload Server</button>


Events
------

We also provide a Event system out of the box. It is up to you if you want to
extend your application with events. If you decide to use it, then you
just need to add in specific places in your code the :func:`emit_event` function
with the name of your event and optionally the data which can be modified by a
plugin::

    from flask.ext.plugins import emit_event

    emit_event("before-data-rendered", data)

and than you can add a callback (e.q. in your plugin setup method)::

    from flask.ext.plugins import connect_event

    def do_before_data_rendered(data):
        return "returning modified data"

    connect_event("before-data-rendered", do_before_data_rendered)


Of course you can also do that in your templates - For this we have already
added :func:`emit_event` to your jinja env context. So you just need to call it
in the template::

    {{ emit_event("before-data-rendered") }}



If you want to see a fully working example, please check it out
`here <https://github.com/sh4nks/flask-plugins/tree/master/example>`_.


The info.json File
==================

Below are shown all available fields a plugin can use. Of course, it always
depends if the application, that uses this extension, needs so much information
about a plugin. The only really required fields are marked with **required**.


``identifier``: **required**
    The plugin's identifier. It should be a Python identifier (starts with a
    letter or underscore, the rest can be letters, underscores, or numbers)
    and should match the name of the plugin's folder.

``name``: **required**
    A human-readable name for the plugin.

``author``: **required**
    The name of the plugin's author, that is, you. It does not have to include
    an e-mail address, and should be displayed verbatim.

``description``
    A description of the plugin in a few sentences. If you can write multiple
    languages, you can include additional fields in the form
    ``description_lc``, where ``lc`` is a two-letter language code like ``es``
    or ``de``. They should contain the description, but in the indicated
    language.

``description_lc``
    This is a dictionary of localized versions of the description.
    The language codes are all lowercase, and the ``en`` key is
    preloaded with the base description.

``website``
    The URL of the plugin's Web site. This can be a Web site specifically for
    this plugin, Web site for a collection of plugins that includes this plugin,
    or just the author's Web site.

``license``
    A simple phrase indicating your plugin's license, like ``GPL``,
    ``MIT/X11``, ``Public Domain``, or ``Creative Commons BY-SA 3.0``. You
    can put the full license's text, usually a ``LICENSE`` file, in the
    plugins root directory.

``license_url``
    A URL pointing to the license text online.

``version``
    This is simply to make it easier to distinguish between what version
    of your plugin people are using. It's up to the theme/layout to decide
    whether or not to show this, though.

``options``
    Any additional options. These are entirely application-specific,
    and may determine other aspects of the application's behavior.


API Documentation
=================

.. autofunction:: get_enabled_plugins

.. autofunction:: get_all_plugins

.. autofunction:: get_plugin_from_all

.. autofunction:: get_plugin

The Plugin Class
----------------

Every ``Plugin`` should implement this class. It is used to get plugin specific
data. and the :class:`PluginManager` tries call the methods which are stated below.

.. autoclass:: Plugin
  :members:
  :special-members:
  :exclude-members: __weakref__


Plugin System
-------------

.. autoclass:: PluginManager
  :members:
  :special-members:
  :exclude-members: __weakref__


Event System
------------

.. autoclass:: EventManager
  :members:
  :special-members:
  :exclude-members: __weakref__


.. autofunction:: emit_event

.. autofunction:: connect_event

.. autofunction:: iter_listeners

.. _example application: https://github.com/sh4nks/flask-plugins/tree/master/example


.. Changelog
.. =========

.. include:: ../CHANGES


License
=======

.. include:: ../LICENSE


Authors
=======

.. include:: ../AUTHORS
