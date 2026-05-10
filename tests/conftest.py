import os

import flask
import pytest

from tests.test_pluginmanager import PluginManager


@pytest.fixture
def app(request):
    app = flask.Flask(__name__)
    app.testing = True
    return app


@pytest.fixture
def test1_plugin(app):
    """Provides the 'test1' plugin and ensures it is enabled after the test."""
    plugin_manager = PluginManager(app)
    plugin = plugin_manager.all_plugins["test1"]
    yield plugin
    # Teardown: ensure 'test1' is enabled for subsequent tests
    disabled_file = os.path.join(plugin.path, "DISABLED")
    if os.path.exists(disabled_file):
        os.remove(disabled_file)
        plugin_manager.load_plugins()
