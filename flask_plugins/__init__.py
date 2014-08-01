# -*- coding: utf-8 -*-
"""
    flask.ext.plugins
    ~~~~~~~~~~~~~~~~~

    The Plugin class that every plugin should implement

    The metadata part (with the info.json file) is inspired by Flask-Themes2
    and the EventManager is taken from Zine.

    :copyright: (c) 2014 by the FlaskBB Team.
    :license: BSD, see LICENSE for more details.
"""
import os
import importlib
from collections import deque
from werkzeug import cached_property
from werkzeug.utils import import_string
from jinja2 import Markup
from flask import current_app, json
from ._compat import itervalues, iteritems


class PluginError(Exception):
    pass


def get_plugin(identifier):
    """Returns a plugin instance from the enabled plugins for the given name."""
    return current_app.plugin_manager.plugins[identifier]


def get_plugin_from_all(identifier):
    """Returns a plugin instance from all plugins (includes also the disabled
    ones) for the given name.
    """
    return current_app.plugin_manager.all_plugins[identifier]


def get_plugins_list():
    """Returns all enabled plugins as a list"""
    return current_app.plugin_manager.plugins.values()


def get_all_plugins():
    """Returns all plugins as a list including the disabled ones."""
    return current_app.plugin_manager.all_plugins.values()


class Plugin(object):
    """Every plugin should implement this class. It handles the registration
    for the plugin hooks, creates or modifies additional relations or
    registers plugin specific thinks
    """

    #: If setup is called, this will be set to ``True``.
    enabled = False

    def __init__(self, path):
        #: The plugin's root path. All the files in the plugin are under this
        #: path.
        self.path = os.path.abspath(path)

        with open(os.path.join(path, 'info.json')) as fd:
            self.info = i = json.load(fd)

        #: The plugin's name, as given in info.json. This is the human
        #: readable name.
        self.name = i['name']

        #: The plugin's identifier. This is an actual Python identifier,
        #: and in most situations should match the name of the directory the
        #: plugin is in.
        self.identifier = i['identifier']

        #: The human readable description. This is the default (English)
        #: version.
        self.description = i.get('description')

        #: This is a dictionary of localized versions of the description.
        #: The language codes are all lowercase, and the ``en`` key is
        #: preloaded with the base description.
        self.localized_desc = dict(
            (k.split('_', 1)[1].lower(), v) for k, v in i.items()
            if k.startswith('description_')
        )
        self.localized_desc.setdefault('en', self.description)

        #: The author's name, as given in info.json. This may or may not
        #: include their email, so it's best just to display it as-is.
        self.author = i['author']

        #: A short phrase describing the license, like "GPL", "BSD", "Public
        #: Domain", or "Creative Commons BY-SA 3.0".
        self.license = i.get('license')

        #: A URL pointing to the license text online.
        self.license_url = i.get('license_url')

        #: The URL to the plugin's or author's Web site.
        self.website = i.get('website')

        #: The plugin's version string.
        self.version = i.get('version')

        #: Any additional options. These are entirely application-specific,
        #: and may determine other aspects of the application's behavior.
        self.options = i.get('options', {})

    @cached_property
    def license_text(self):
        """
        The contents of the theme's license.txt file, if it exists. This is
        used to display the full license text if necessary. (It is `None` if
        there was not a license.txt.)
        """
        lt_path = os.path.join(self.path, 'license.txt')
        if os.path.exists(lt_path):
            with open(lt_path) as fd:
                return fd.read()
        else:
            return None

    def setup(self):  # pragma: no cover
        """This method is used to register all things that the plugin wants to
        register.
        """
        pass

    def install(self):  # pragma: no cover
        """Installs the things that must be installed in order to have a
        fully and correctly working plugin. For example, something that needs
        to be installed can be a relation and/or modify a existing relation.
        """
        pass

    def uninstall(self):  # pragma: no cover
        """Uninstalls all the things which were previously installed by
        `install()`. A Plugin must override this method.
        """
        pass


class PluginManager(object):
    """Collects all Plugins and maps the metadata to the plugin"""

    def __init__(self, app=None, **kwargs):
        """Initializes the PluginManager. It is also possible to initialize the
        PluginManager via a factory. For example::

            plugin_manager = PluginManager()
            plugin_manager.init_app(app)

        :param app: The flask application.

        :param plugin_folder: The plugin folder where the plugins resides.

        :param base_app_folder: The base folder for the application. It is used
                                to build the plugins package name.
        """
        # All enabled plugins
        self._plugins = None

        # All plugins - including the disabled ones
        self._all_plugins = None

        # All available plugins including the disabled ones
        self._available_plugins = dict()

        # All found plugins
        self._found_plugins = dict()

        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, base_app_folder=None, plugin_folder="plugins"):
        self._event_manager = EventManager(app)

        app.plugin_manager = self
        app.jinja_env.globals["emit_event"] = self._event_manager.template_emit

        self.app = app

        if base_app_folder is None:
            base_app_folder = self.app.root_path.split(os.sep)[-1]

        self.plugin_folder = os.path.join(self.app.root_path, plugin_folder)
        self.base_plugin_package = ".".join(
            [base_app_folder, plugin_folder]
        )

        self.setup_plugins()

    @property
    def all_plugins(self):
        """Returns all plugins including disabled ones."""
        if self._all_plugins is None:
            self.load_plugins()
        return self._all_plugins

    @property
    def plugins(self):
        """Returns all enabled plugins as a dictionary. You still need to
        call the setup method to fully enable them."""
        if self._plugins is None:
            self.load_plugins()
        return self._plugins

    def load_plugins(self):
        """Loads all plugins. They are still disabled.
        Returns a list with all loaded plugins. They should now be accessible
        via self.plugins.
        """
        self._plugins = {}
        self._all_plugins = {}
        for plugin_name, plugin_package in iteritems(self.find_plugins()):

            try:
                plugin_class = import_string(
                    "{}.{}".format(plugin_package, plugin_name)
                )
            except ImportError:
                raise PluginError(
                    "Couldn't import {} Plugin. Please check if the __plugin__ "
                    "variable is set correctly.".format(plugin_name)
                )

            plugin_path = os.path.join(
                self.plugin_folder,
                os.path.basename(plugin_package.replace(".", "/"))
            )

            plugin_instance = plugin_class(plugin_path)

            try:
                if self._available_plugins[plugin_name]:
                    self._plugins[plugin_instance.identifier] = plugin_instance
            except KeyError:
                pass

            self._all_plugins[plugin_instance.identifier] = plugin_instance

    def find_plugins(self):
        """Find all possible plugins in the plugin folder."""
        for item in os.listdir(self.plugin_folder):
            if os.path.isdir(os.path.join(self.plugin_folder, item)) \
                    and os.path.exists(
                        os.path.join(self.plugin_folder, item, "__init__.py")):

                plugin = ".".join([self.base_plugin_package, item])

                # Same like from exammple.plugins.pluginname import __plugin__
                tmp = importlib.import_module(plugin)

                try:
                    # Add the plugin to the available plugins if the plugin
                    # isn't disabled
                    if not os.path.exists(
                            os.path.join(self.plugin_folder, item, "DISABLED")):

                        self._available_plugins[tmp.__plugin__] = \
                            "{}".format(plugin)

                    self._found_plugins[tmp.__plugin__] = \
                        "{}".format(plugin)

                except AttributeError:
                    pass

        return self._found_plugins

    def setup_plugins(self):  # pragma: no cover
        """Runs the setup for all plugins. It is recommended to run this
        after the PluginManager has been initialized.
        """
        for plugin in itervalues(self.plugins):
            with self.app.app_context():
                plugin.setup()
                plugin.enabled = True

    def install_plugins(self, plugins=None):
        """Install all or selected plugins.

        :param plugins: An iterable with plugins. If no plugins are passed
                        it will try to install all plugins.
        """
        for plugin in plugins or itervalues(self.plugins):
            with self.app.app_context():
                plugin.install()

    def uninstall_plugins(self, plugins=None):
        """Uninstall the plugin.

        :param plugins: An iterable with plugins. If no plugins are passed
                        it will try to uninstall all plugins.
        """
        for plugin in plugins or itervalues(self.plugins):
            with self.app.app_context():
                plugin.uninstall()


def connect_event(event, callback, position='after'):
    """Connect a callback to an event.  Per default the callback is
    appended to the end of the handlers but handlers can ask for a higher
    privilege by setting `position` to ``'before'``.

    Example usage::

        def on_before_metadata_assembled(metadata):
            metadata.append('<!-- IM IN UR METADATA -->')

        # And in your setup() method do this:
            connect_event('before-metadata-assembled',
                           on_before_metadata_assembled)
    """
    current_app.plugin_manager._event_manager.connect(event, callback, position)


def emit_event(event, *args, **kwargs):
    """Emit a event and return a list of event results.  Each called
    function contributes one item to the returned list.

    This is equivalent to the following call to :func:`iter_listeners`::

        result = []
        for listener in iter_listeners(event):
            result.append(listener(*args, **kwargs))
    """
    return [x(*args, **kwargs) for x in
            current_app.plugin_manager._event_manager.iter(event)]


def iter_listeners(event):
    """Return an iterator for all the listeners for the event provided."""
    return current_app.plugin_manager._event_manager.iter(event)


class EventManager(object):
    """Helper class that handles event listeners and event emitting.

    This is *not* a public interface. Always use the `emit_event` or
    `connect_event` or the `iter_listeners` functions to access it.
    """

    def __init__(self, app):
        self.app = app
        self._listeners = {}
        self._last_listener = 0

    def connect(self, event, callback, position='after'):
        """Connect a callback to an event."""
        assert position in ('before', 'after'), 'invalid position'
        listener_id = self._last_listener
        event = intern(event)
        if event not in self._listeners:
            self._listeners[event] = deque([callback])
        elif position == 'after':
            self._listeners[event].append(callback)
        elif position == 'before':
            self._listeners[event].appendleft(callback)
        self._last_listener += 1
        return listener_id

    def remove(self, event, callback):
        """Remove a callback again."""
        try:
            self._listeners[event].remove(callback)
        except (KeyError, ValueError):
            pass

    def iter(self, event):
        """Return an iterator for all listeners of a given name."""
        if event not in self._listeners:
            return iter(())
        return iter(self._listeners[event])

    def template_emit(self, event, *args, **kwargs):
        """Emits events for the template context."""
        results = []
        for f in self.iter(event):
            rv = f(*args, **kwargs)
            if rv is not None:
                results.append(rv)
        return Markup(TemplateEventResult(results))


class TemplateEventResult(list):
    """A list subclass for results returned by the event listener that
    concatenates the results if converted to string, otherwise it works
    exactly like any other list.
    """

    def __init__(self, items):
        list.__init__(self, items)

    def __unicode__(self):
        return u''.join(map(unicode, self))

    def __str__(self):
        return unicode(self).encode('utf-8')
