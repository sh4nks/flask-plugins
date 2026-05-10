import os

import pytest

from flask_plugins import get_all_plugins
from flask_plugins import get_enabled_plugins
from flask_plugins import get_plugin
from flask_plugins import get_plugin_from_all
from flask_plugins import PluginError
from flask_plugins import PluginManager


def test_class_init(app):
    plugin_manager = PluginManager(app)
    assert (
        hasattr(app, "extensions")
        and plugin_manager is app.extensions["plugin_manager"]
    )


def test_init_app(app):
    plugin_manager = PluginManager()
    assert app.extensions == {}

    plugin_manager.init_app(app)
    assert (
        hasattr(app, "extensions")
        and plugin_manager is app.extensions["plugin_manager"]
    )


def test_find_plugins(app):
    plugin_manager = PluginManager(app)
    found_plugins = plugin_manager.find_plugins()
    assert len(found_plugins) == 3
    expected = ["TestOnePlugin", "TestTwoPlugin", "TestThreePlugin"]
    assert sorted(found_plugins) == sorted(expected)


def test_plugins_property(app):
    plugin_manager = PluginManager(app)
    plugin_manager._plugins = None
    assert plugin_manager._plugins is None
    assert sorted(plugin_manager.plugins.keys()) == ["test1", "test2"]


def test_all_plugins_property(app):
    plugin_manager = PluginManager(app)
    plugin_manager._all_plugins = None
    assert plugin_manager._all_plugins is None
    assert sorted(plugin_manager.all_plugins.keys()) == ["test1", "test2", "test3"]


def test_get_enabled_plugins(app):
    plugin_manager = PluginManager(app)
    with app.test_request_context():
        plugins = get_enabled_plugins()
    assert set(plugins) == set(plugin_manager.plugins.values())


def test_get_all_plugins(app):
    plugin_manager = PluginManager(app)
    with app.test_request_context():
        plugins = get_all_plugins()
    assert len(plugins) == 3


def test_get_plugin(app):
    plugin_manager = PluginManager(app)
    with app.test_request_context():
        plugin = get_plugin("test1")
    assert plugin == plugin_manager.plugins["test1"]


def test_get_plugin_from_all(app):
    plugin_manager = PluginManager(app)
    with app.test_request_context():
        plugin = get_plugin_from_all("test3")
    assert not plugin.enabled


def test_wrong_plugin_folder(app):
    plugin_manager = PluginManager()
    # Tests if a PluginError is raised for invalid plugin definitions
    with pytest.raises(PluginError):
        plugin_manager.init_app(app, plugin_folder="plugs")


def test_plugin_disable_and_enable(app, test1_plugin):
    PluginManager(app)

    # Test individual plugin methods
    assert not test1_plugin.disable()  # returns False because it was enabled
    assert test1_plugin.enable()  # returns True because it was disabled


def test_plugin_setup_install_uninstall(app, test1_plugin):
    PluginManager(app)

    test1_plugin.setup()
    assert test1_plugin.setup_called

    test1_plugin.install()
    assert test1_plugin.install_called

    test1_plugin.uninstall()
    assert test1_plugin.uninstall_called


def test_manager_bulk_actions(app):
    plugin_manager = PluginManager(app)
    plugin_manager.load_plugins()

    with app.test_request_context():
        plugin = plugin_manager.plugins["test1"]

        assert not plugin.setup_called
        plugin_manager.setup_plugins()
        assert plugin.setup_called

        plugin_manager.install_plugins()
        assert plugin.install_called

        plugin_manager.uninstall_plugins()
        assert plugin.uninstall_called


def test_manager_enable_disable_logic(app, test1_plugin):
    plugin_manager = PluginManager(app)

    assert test1_plugin.enabled
    assert plugin_manager.disable_plugins([test1_plugin]) == 1
    assert os.path.exists(os.path.join(test1_plugin.path, "DISABLED"))

    plugin_manager.enable_plugins([test1_plugin])
    assert test1_plugin.enabled
