from flask import current_app
from flask import Flask
from flask import redirect
from flask import render_template
from flask import url_for

from flask_plugins import emit_event
from flask_plugins import get_enabled_plugins
from flask_plugins import get_plugin
from flask_plugins import Plugin
from flask_plugins import PluginManager


# to demonstrate how easy it is to create your own plugin class for your plugins
class AppPlugin(Plugin):
    def register_blueprint(self, blueprint, **kwargs):
        """Registers a blueprint."""
        current_app.register_blueprint(blueprint, **kwargs)


# Default Settings
SECRET_KEY = "this-key-is-not-secure"

# Initialize flask and register the example blueprint
app = Flask(__name__)
app.config.from_object(__name__)

# Initialize the plugin manager
plugin_manager = PluginManager(app)


@app.route("/")
def index():
    emit_event("after_navigation")

    return render_template("index.html", plugins=get_enabled_plugins())


@app.route("/disable/<plugin>")
def disable(plugin):
    plugin = get_plugin(plugin)
    plugin_manager.disable_plugins([plugin])
    return redirect(url_for("index"))


@app.route("/enable/<plugin>")
def enable(plugin):
    plugin = get_plugin(plugin)
    plugin_manager.enable_plugins([plugin])
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
