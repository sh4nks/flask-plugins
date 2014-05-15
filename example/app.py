from flask import Flask, render_template, redirect, url_for, current_app

from flask.ext.plugins import PluginManager, get_plugins_list, get_plugin, \
    Plugin, emit_event


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

    return render_template("index.html", plugins=get_plugins_list())


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
