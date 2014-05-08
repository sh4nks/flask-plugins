# -*- coding: utf-8 -*-
"""
    flask.ext.plugins
    ~~~~~~~~~~~~~~~~~

    The Plugin class that every plugin should implement

    :copyright: (c) 2014 by the FlaskBB Team.
    :license: BSD, see LICENSE for more details.
"""
import os
import importlib
from werkzeug.utils import import_string
from flask import current_app
from ._compat import itervalues


class PluginError(Exception):
    pass


def get_plugin(name):
    return current_app.plugin_manager.plugins[name]


def get_plugins_list():
    return current_app.plugin_manager.plugins.values()


class Plugin(object):
    """Every plugin should implement this class. It handles the registration
    for the plugin hooks, creates or modifies additional relations or
    registers plugin specific thinks"""

    #: The name of the plugin. This name is displayed in the admin panel
    name = None

    #: The author of the plugin
    author = ""

    #: The license of the plugin
    license = ""

    #: A small description of the plugin.
    description = ""

    #: The version of the plugin"""
    version = "0.0.0"

    def setup(self):  # pragma: no cover
        """This method is used to register all things that needs to be done
        before the app is serving requests. A good example for that are
        Blueprints.
        """
        pass

    def enable(self):
        """Enable the plugin. For example, registers the hooks."""
        raise NotImplementedError("{} has not implemented the "
                                  "enable method".format(self.name))

    def disable(self):
        """Disable the plugin."""
        raise NotImplementedError("{} has not implemented the "
                                  "disable method".format(self.name))

    def install(self):
        """The plugin should specify here what needs to be installed like the
        the models. """
        raise NotImplementedError("{} has not implemented the "
                                  "install method".format(self.name))

    def uninstall(self):
        """Uninstalls the plugin and deletes the things that
        the plugin has installed."""
        raise NotImplementedError("{} has not implemented the "
                                  "uninstall method".format(self.name))


class PluginManager(object):

    def __init__(self, app=None, **kwargs):
        """Initializes the PluginManager. It is also possible to initialize the
        PluginManager via a factory. For example::

            plugin_manager = PluginManager()
            plugin_manager.init_app(app)

        :param app: The flask application. It is needed to do plugin
                    specific things like registering additional views or
                    doing things where the application context is needed.

        :param plugin_folder: The plugin folder where the plugins resides.

        :param base_app_folder: The base folder for the application. It is used
                                to build the plugins package name.
        """
        # All loaded plugins
        self._plugins = None

        # All found plugins
        self._found_plugins = []

        # TODO: Use a datastore to store the status of the plugins
        # and fallback to a simple memory store if no datastore is choosen
        self._enabled_plugins = set()
        self._installed_plugins = set()

        if app is not None:
            self.init_app(app, **kwargs)

    def init_app(self, app, base_app_folder=None,
                 plugin_folder="plugins"):
        app.plugin_manager = self

        self.app = app

        if base_app_folder is None:
            base_app_folder = self.app.root_path.split("/")[-1]

        self.plugin_folder = os.path.join(self.app.root_path, plugin_folder)
        self.base_plugin_package = ".".join(
            [base_app_folder, plugin_folder]
        )

    @property
    def plugins(self):
        """Returns all loaded plugins as a dictionary. You still need to
        enable them."""
        if self._plugins is None:
            self.load_plugins()
        return self._plugins

    def load_plugins(self):
        """Loads all plugins. They are still disabled.
        Returns a list with all loaded plugins. They should now be accessible
        via self.plugins.
        """
        self._plugins = {}
        for plugin_class in self.iter_plugins():
            plugin_instance = plugin_class()
            self._plugins[plugin_instance.name] = plugin_instance

    def iter_plugins(self):
        """Iterates over all possible plugins found in ``self.find_plugins()``,
        imports them and if the import succeeded it will yield the plugin class.
        """
        for plugin in self.find_plugins():
            try:
                plugin_class = import_string(plugin)
            except ImportError:
                raise PluginError(
                    "Couldn't import {} Plugin. Please check if the __plugin__ "
                    "variable is set correctly. Skipping...".format(plugin)
                )

            if plugin_class is not None:
                yield plugin_class

    def find_plugins(self):
        """Find all possible plugins in the plugin folder."""
        for item in os.listdir(self.plugin_folder):
            if os.path.isdir(os.path.join(self.plugin_folder, item)) and \
                    os.path.exists(
                        os.path.join(self.plugin_folder, item, "__init__.py")):

                plugin = ".".join([self.base_plugin_package, item])

                # Same like from exammple.plugins.pluginname import __plugin__
                tmp = importlib.import_module(plugin)

                try:
                    plugin = "{}.{}".format(plugin, tmp.__plugin__)
                    self._found_plugins.append(plugin)
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

    def install_plugins(self, plugins=None):
        """Install all or selected plugins.

        :param plugins: An iterable with plugins. If no plugins are passed
                        it will try to install all plugins.
        """
        for plugin in plugins or itervalues(self.plugins):
            if plugin not in self._installed_plugins:
                with self.app.app_context():
                    plugin.install()

                self._installed_plugins.add(plugin)

    def uninstall_plugins(self, plugins=None):
        """Uninstall the plugin.

        :param plugins: An iterable with plugins. If no plugins are passed
                        it will try to uninstall all plugins.
        """
        for plugin in plugins or itervalues(self.plugins):
            if plugin in self._installed_plugins:
                with self.app.app_context():
                    plugin.uninstall()

                self._installed_plugins.remove(plugin)

    def enable_plugins(self, plugins=None):
        """Enable all or selected plugins.

        :param plugins: An iterable with plugins. If no plugins are passed
                        it will try to enable all plugins.
        """
        for plugin in plugins or itervalues(self.plugins):
            # check if the plugin is already enabled
            if plugin not in self._enabled_plugins:
                with self.app.app_context():
                    plugin.enable()

                self._enabled_plugins.add(plugin)

    def disable_plugins(self, plugins=None):
        """Disable all or selected plugins.

        :param plugins: An iterable with plugins. If no plugins are passed
                        it will try to disable all plugins.
        """
        for plugin in plugins or itervalues(self.plugins):
            # only disable a plugin if it is enabled
            if plugin in self._enabled_plugins:
                with self.app.app_context():
                    plugin.disable()

                self._enabled_plugins.remove(plugin)


class HookManager(object):
    """Manages all available hooks.

    A new hook can be created like this::

        hooks.new("testHook")

    To add a callback to the hook you need to do that::

        hooks.add("testHook", test_callback)

    If you want to use the last method, you'd also need to pass a callback over
    to the ``add`` method.
    Then you might want to add somewhere in your code the ``caller`` where all
    registered callbacks for the specified hook are going to be called.
    For example::

        def hello():
            do_stuff_here()

            hooks.call("testHook")

            do_more_stuff_here()
    """

    def __init__(self):
        self.hooks = {}

    def new(self, name, hook=None):
        """Creates a new hook.

        :param name: The name of the hook.

        :param hook: The Hook class. Can be overridden if needed. Defaults to
                     Hook().
        """
        if name not in self.hooks:
            self.hooks[name] = hook or Hook()

    def add(self, name, callback):
        """Adds a callback to the hook.

        :param name: The name of the hook.

        :param callback: The callback which should be added to the hook.
        """
        return self.hooks[name].add(callback)

    def remove(self, name, callback):
        """Removes a callback from the hook.

        :param name: The name of the hook.

        :param callback: The callback which should be removed
        """
        self.hooks[name].remove(callback)

    def call(self, name, *args, **kwargs):
        """Calls all callbacks from a named hook with the given arguments.

        :param name: The name of the hook.
        """
        if len(self.hooks[name].callbacks) > 0:
            return self.hooks[name].call(*args, **kwargs)

        # Return an empty string. This is neccessary if you are running
        # template hooks because we don't want that "None" is printed in the
        # templates.
        return ""


class Hook(object):
    """Represents a hook."""

    def __init__(self):
        self.callbacks = []

    def add(self, callback):
        """Adds a callback to a hook"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
        return callback

    def remove(self, callback):
        """Removes a callback from a hook"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)

    def call(self, *args, **kwargs):
        """Runs all callbacks for the hook."""
        for callback in self.callbacks:
            return callback(*args, **kwargs)
