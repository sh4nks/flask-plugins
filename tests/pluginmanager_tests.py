
import unittest

from flask import Flask
from flask.ext.plugins import PluginManager, PluginError, get_plugins_list, \
    get_plugin


class InitializationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True

    def test_init_app(self):
        plugin_manager = PluginManager()
        plugin_manager.init_app(self.app)

        self.assertIsInstance(plugin_manager, PluginManager)

    def test_class_init(self):
        plugin_manager = PluginManager(self.app)
        self.assertIsInstance(plugin_manager, PluginManager)


class PluginManagerTests(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.plugin_manager = PluginManager()
        self.plugin_manager.init_app(self.app)

    def test_find_plugins(self):
        found_plugins = self.plugin_manager.find_plugins()
        self.assertEqual(len(found_plugins), 2)
        expected_plugins = ['tests.plugins.test1.TestOnePlugin',
                            'tests.plugins.test2.TestTwoPlugin']
        self.assertEquals(sorted(found_plugins), expected_plugins)

    def test_load_plugins(self):
        self.assertEquals(self.plugin_manager._plugins, None)

        self.plugin_manager.load_plugins()

        self.assertEquals(
            sorted(self.plugin_manager.plugins.keys()), ["Test One", "Test Two"]
        )


class PluginManagerGetPlugins(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.plugin_manager = PluginManager()
        self.plugin_manager.init_app(self.app)

    def test_get_plugins_list(self):
        with self.app.test_request_context():
            plugins = get_plugins_list()

        self.assertEquals(plugins, self.plugin_manager.plugins.values())

    def test_get_plugin(self):
        with self.app.test_request_context():
            plugin = get_plugin("Test One")

        self.assertEquals(plugin, self.plugin_manager.plugins["Test One"])


class PluginManagerOtherDirectoryTests(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.plugin_manager = PluginManager()
        self.plugin_manager.init_app(self.app, plugin_folder="plugs")

    def test_iter_plugins(self):
        # should raise an exception because the plugin in the "plugs" folder
        # have set the __plugin__ variable not correctly.
        with self.assertRaises(PluginError):
            self.plugin_manager.plugins


class PluginManagerOnePluginTests(unittest.TestCase):
    """Tests the plugin.setup(), plugin.enabled()... methods"""
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.plugin_manager = PluginManager()
        self.plugin_manager.init_app(self.app)
        self.plugin_manager.load_plugins()

    def test_plugin_setup(self):
        plugin = self.plugin_manager.plugins["Test One"]
        plugin.setup()
        self.assertTrue(plugin.setup_called)

    def test_plugin_enabled(self):
        plugin = self.plugin_manager.plugins["Test One"]
        plugin.enable()
        self.assertTrue(plugin.enable_called)

    def test_plugin_disabled(self):
        plugin = self.plugin_manager.plugins["Test One"]
        plugin.disable()
        self.assertTrue(plugin.disable_called)

    def test_plugin_install(self):
        plugin = self.plugin_manager.plugins["Test One"]
        plugin.install()
        self.assertTrue(plugin.install_called)

    def test_plugin_uninstall(self):
        plugin = self.plugin_manager.plugins["Test One"]
        plugin.uninstall()
        self.assertTrue(plugin.uninstall_called)


class PluginManagerAllPluginsTests(unittest.TestCase):
    """Tests the plugin_manager.install_plugins(),... methods"""
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.plugin_manager = PluginManager()
        self.plugin_manager.init_app(self.app)
        self.plugin_manager.load_plugins()

    def test_plugins_all_enabled(self):
        self.plugin_manager.enable_plugins()
        self.assertEquals(self.plugin_manager._enabled_plugins,
                          set(self.plugin_manager.plugins.values()))

    def test_plugins_all_disabled(self):
        # just to be sure that every plugin is enabled
        self.plugin_manager.enable_plugins()

        # now disable all plugins
        self.plugin_manager.disable_plugins()

        self.assertEquals(self.plugin_manager._enabled_plugins, set())

    def test_plugins_all_install(self):
        self.plugin_manager.install_plugins()

        self.assertEquals(self.plugin_manager._installed_plugins,
                          set(self.plugin_manager.plugins.values()))

    def test_plugins_all_uninstall(self):
        self.plugin_manager.install_plugins()

        self.plugin_manager.uninstall_plugins()

        self.assertEquals(self.plugin_manager._installed_plugins, set())

    ##########
    # now test this with a single plugin
    def test_plugins_single_enabled(self):
        plugin = self.plugin_manager.plugins["Test One"]
        self.plugin_manager.enable_plugins([plugin])

        self.assertEquals(len(self.plugin_manager._enabled_plugins), 1)

    def test_plugins_single_disabled(self):
        plugin = self.plugin_manager.plugins["Test One"]
        self.plugin_manager.disable_plugins([plugin])

        self.assertEquals(len(self.plugin_manager._enabled_plugins), 0)

    def test_plugins_single_install(self):
        plugin = self.plugin_manager.plugins["Test One"]
        self.plugin_manager.install_plugins([plugin])

        self.assertEquals(len(self.plugin_manager._installed_plugins), 1)

    def test_plugins_single_uninstall(self):
        plugin = self.plugin_manager.plugins["Test One"]
        self.plugin_manager.uninstall_plugins([plugin])

        self.assertEquals(len(self.plugin_manager._installed_plugins), 0)
