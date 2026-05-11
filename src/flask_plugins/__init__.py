"""
flask_plugins
~~~~~~~~~~~~~

The Plugin class that every plugin should implement

The metadata part (with the info.json file) is inspired by Flask-Themes2
and the EventManager is taken from Zine.

:copyright: (c) 2026 by the FlaskBB Team.
:license: BSD, see LICENSE for more details.
"""

import importlib
import os
import sys
from collections import deque

from flask import json
from flask.app import Flask
from flask.globals import current_app
from markupsafe import Markup
from werkzeug.utils import cached_property
from werkzeug.utils import import_string

__version__ = "2.0.0"
__author__ = "Peter Justin"


class PluginError(Exception):
    pass


def get_plugin(identifier):
    """Returns a plugin instance from the enabled plugins for the given
    name.
    """
    pm = _get_pm()
    if pm is None or pm.plugins is None:
        return None

    return pm.plugins[identifier]


def get_plugin_from_all(identifier):
    """Returns a plugin instance from all plugins (includes also the disabled
    ones) for the given name.
    """
    pm = _get_pm()
    if pm is None or pm.all_plugins is None:
        return None

    return pm.all_plugins[identifier]


def get_enabled_plugins():
    """Returns all enabled plugins as a list"""
    pm = _get_pm()
    if pm is None or pm.plugins is None:
        return None

    return pm.plugins.values()


def get_all_plugins():
    """Returns all plugins as a list including the disabled ones."""
    pm = _get_pm()
    if pm is None or pm.all_plugins is None:
        return None

    return pm.all_plugins.values()


class Plugin:
    """Every plugin should implement this class. It handles the registration
    for the plugin hooks, creates or modifies additional relations or
    registers plugin specific thinks
    """

    #: If setup is called, this will be set to ``True``.
    enabled = False

    def __init__(self, path: str):
        #: The plugin's root path. All the files in the plugin are under this
        #: path.
        self.path: str = os.path.abspath(path)

        with open(os.path.join(path, "info.json")) as fd:
            self.info = i = json.load(fd)

        #: The plugin's name, as given in info.json. This is the human
        #: readable name.
        self.name: str = i["name"]

        #: The plugin's identifier. This is an actual Python identifier,
        #: and in most situations should match the name of the directory the
        #: plugin is in.
        self.identifier: str = i["identifier"]

        #: The human readable description. This is the default (English)
        #: version.
        self.description: str | None = i.get("description")

        #: This is a dictionary of localized versions of the description.
        #: The language codes are all lowercase, and the ``en`` key is
        #: preloaded with the base description.
        self.description_lc: dict[str, str | None] = dict(
            (k.split("_", 1)[1].lower(), v)
            for k, v in i.items()
            if k.startswith("description_")
        )
        self.description_lc.setdefault("en", self.description)

        #: The author's name, as given in info.json. This may or may not
        #: include their email, so it's best just to display it as-is.
        self.author: str | None = i["author"]

        #: A short phrase describing the license, like "GPL", "BSD", "Public
        #: Domain", or "Creative Commons BY-SA 3.0".
        self.license: str | None = i.get("license")

        #: A URL pointing to the license text online.
        self.license_url: str | None = i.get("license_url")

        #: The URL to the plugin's or author's Web site.
        self.website: str | None = i.get("website")

        #: The plugin's version string.
        self.version: str | None = i.get("version")

        #: Any additional options. These are entirely application-specific,
        #: and may determine other aspects of the application's behavior.
        self.options: str | None = i.get("options", {})

    @cached_property
    def license_text(self):
        """
        The contents of the theme's license.txt file, if it exists. This is
        used to display the full license text if necessary. (It is `None` if
        there was not a license.txt.)
        """
        lt_path = os.path.join(self.path, "license.txt")
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

    def enable(self):
        """Enables the plugin by removing the 'DISABLED' file in the plugins
        root directory, calls the ``setup()`` method and sets the plugin state
        to true.
        """
        disabled_file = os.path.join(self.path, "DISABLED")
        try:
            if os.path.exists(disabled_file):
                os.remove(disabled_file)

            if not self.enabled:
                self.enabled = True
        except:
            raise
        return self.enabled

    def disable(self):
        """Disablesthe plugin.

        The app usually has to be restarted after this action because
        plugins _can_ register blueprints and in order to "unregister" them,
        the application object has to be destroyed.
        This is a limitation of Flask and if you want to know more about this
        visit this link: http://flask.pocoo.org/docs/0.10/blueprints/
        """
        disabled_file = os.path.join(self.path, "DISABLED")
        try:
            open(disabled_file, "a").close()
            self.enabled = False
        except:
            raise
        return self.enabled

    def install(self):  # pragma: no cover
        """Installs the things that must be installed in order to
        have a fully and correctly working plugin. For example, something that
        needs to be installed can be a relation and/or modify a existing
        relation.
        """
        pass

    def uninstall(self):  # pragma: no cover
        """Uninstalls all the things which were previously
        installed by `install()`. A Plugin must override this method.
        """
        pass


class PluginManager:
    """Collects all Plugins and maps the metadata to the plugin"""

    def __init__(self, app: Flask | None = None, **kwargs):
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
        self._plugins: dict[str, Plugin] | None = None

        # All plugins - including the disabled ones
        self._all_plugins: dict[str, Plugin] | None = None

        # All available plugins including the disabled ones
        self._available_plugins: dict[str, str] = dict()

        # All found plugins
        self._found_plugins: dict[str, str] = dict()

        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, base_app_folder=None, plugin_folder="plugins"):
        self._event_manager = EventManager()
        app.jinja_env.globals["emit_event"] = self._event_manager.template_emit

        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["plugin_manager"] = self

        if base_app_folder is None:
            base_app_folder = app.root_path.split(os.sep)[-1]

        self.plugin_folder = os.path.join(app.root_path, plugin_folder)
        self.base_plugin_package = ".".join([base_app_folder, plugin_folder])

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
        for plugin_name, plugin_package in self.find_plugins().items():
            try:
                plugin_class = import_string(f"{plugin_package}.{plugin_name}")
            except ImportError as e:
                raise PluginError(
                    f"Couldn't import {plugin_name} Plugin. Please check if the "
                    "__plugin__ variable is set correctly."
                ) from e

            plugin_path = os.path.join(
                self.plugin_folder, os.path.basename(plugin_package.replace(".", "/"))
            )

            plugin_instance: Plugin = plugin_class(plugin_path)

            try:
                if self._available_plugins[plugin_name]:
                    self._plugins[plugin_instance.identifier] = plugin_instance
            except KeyError:
                pass

            self._all_plugins[plugin_instance.identifier] = plugin_instance

    def find_plugins(self):
        """Find all possible plugins in the plugin folder."""
        for item in os.listdir(self.plugin_folder):
            if os.path.isdir(os.path.join(self.plugin_folder, item)) and os.path.exists(
                os.path.join(self.plugin_folder, item, "__init__.py")
            ):
                plugin = ".".join([self.base_plugin_package, item])

                # Same like from exammple.plugins.pluginname import __plugin__
                tmp = importlib.import_module(plugin)

                try:
                    # Add the plugin to the available plugins if the plugin
                    # isn't disabled
                    if not os.path.exists(
                        os.path.join(self.plugin_folder, item, "DISABLED")
                    ):
                        self._available_plugins[tmp.__plugin__] = f"{plugin}"

                    self._found_plugins[tmp.__plugin__] = f"{plugin}"

                except AttributeError:
                    pass

        return self._found_plugins

    def setup_plugins(self):  # pragma: no cover
        """Runs the setup for all enabled plugins. Should be run after the
        PluginManager has been initialized. Sets the state of the plugin to
        enabled.
        """
        if not self.plugins:
            return

        for plugin in self.plugins.values():
            plugin.enabled = True
            plugin.setup()

    def install_plugins(self, plugins: dict[str, Plugin] | None = None):
        """Installs one or more plugins.

        :param plugins: An iterable with plugins. If no plugins are passed
                        it will try to install all plugins.
        """
        if not self.plugins and not plugins:
            return

        values = []
        if plugins:
            values = plugins.values()
        elif self.plugins:
            values = self.plugins.values()

        for plugin in values:
            with current_app.app_context():
                plugin.install()

    def uninstall_plugins(self, plugins: dict[str, Plugin] | None = None):
        """Uninstalls one or more plugins.

        :param plugins: An iterable with plugins. If no plugins are passed
                        it will try to uninstall all plugins.
        """
        if not self.plugins and not plugins:
            return

        values = []
        if plugins:
            values = plugins.values()
        elif self.plugins:
            values = self.plugins.values()

        for plugin in values:
            with current_app.app_context():
                plugin.uninstall()

    def enable_plugins(self, plugins: list[Plugin] | None = None):
        """Enables one or more plugins.

        It either returns the amount of enabled plugins or
        raises an exception caused by ``os.remove`` which says most likely
        that you can't write on the filesystem.

        :param plugins: An iterable with plugins.
        """
        _enabled_count = 0
        for plugin in plugins or []:
            plugin.enable()
            _enabled_count += 1
        return _enabled_count

    def disable_plugins(self, plugins: list[Plugin] | None = None):
        """Disables one or more plugins.
        It either returns the amount of disabled plugins or
        raises an exception caused by ``open`` which says most likely
        that you can't write on the filesystem.

        The app usually has to be restarted after this action because
        plugins **can** register blueprints and in order to "unregister" them,
        the application object has to be destroyed.
        This is a limitation of Flask and if you want to know more about this
        visit this link: http://flask.pocoo.org/docs/0.10/blueprints/

        :param plugins: An iterable with plugins
        """
        _disabled_count = 0
        for plugin in plugins or []:
            plugin.disable()
            _disabled_count += 1
        return _disabled_count


def connect_event(event, callback, position="after"):
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
    em = _get_em()
    if em is None:
        return iter(())

    em.connect(event, callback, position)


def emit_event(event, *args, **kwargs):
    """Emit a event and return a list of event results.  Each called
    function contributes one item to the returned list.

    This is equivalent to the following call to :func:`iter_listeners`::

        result = []
        for listener in iter_listeners(event):
            result.append(listener(*args, **kwargs))
    """
    em = _get_em()
    if em is None:
        return iter(())

    return [x(*args, **kwargs) for x in em.iter(event)]


def iter_listeners(event):
    """Return an iterator for all the listeners for the event provided."""
    em = _get_em()
    if em is None:
        return iter(())
    return em.iter(event)


class EventManager:
    """Helper class that handles event listeners and event emitting.

    This is *not* a public interface. Always use the `emit_event` or
    `connect_event` or the `iter_listeners` functions to access it.
    """

    def __init__(self):
        self._listeners = {}
        self._last_listener = 0

    def connect(self, event, callback, position="after"):
        """Connect a callback to an event."""
        assert position in ("before", "after"), "invalid position"
        listener_id = self._last_listener
        event = sys.intern(event)
        if event not in self._listeners:
            self._listeners[event] = deque([callback])
        elif position == "after":
            self._listeners[event].append(callback)
        elif position == "before":
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
        return "".join(map(str, self))

    def __str__(self):
        return self.__unicode__()


def _get_pm(app: Flask | None = None, silent: bool = False) -> PluginManager | None:
    """Gets the application-specific Plugin Manager.

    :param app: The Flask application. Defaults to the current app.
    :param silent: If set to True, it will return ``None`` instead of raising
                   a ``RuntimeError``.
    """
    if app is None:
        app = current_app

    if silent and (not app or "plugin_manager" not in app.extensions):
        return None

    if "plugin_manager" not in app.extensions:
        raise RuntimeError("Flask-Plugins not configured against current app")

    return app.extensions["plugin_manager"]


def _get_em(app: Flask | None = None) -> EventManager | None:
    pm = _get_pm(app)
    if pm is None:
        return None

    return pm._event_manager
