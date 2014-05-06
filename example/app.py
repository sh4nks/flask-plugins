from flask import Flask, render_template
from flask.ext.plugins import PluginManager, get_plugins_list
from hooks import hooks

# Default Settings
SECRET_KEY = "this-key-is-not-secure"

# Initialize flask and register the example blueprint
app = Flask(__name__)
app.config.from_object(__name__)

# Initialize the plugin manager
plugin_manager = PluginManager(app)
plugin_manager.enable_plugins()

# to be able to also run hooks in our templates, we need to add the hooks
# manager to jinja's globals.
app.jinja_env.globals.update(hooks=hooks)


@app.route("/")
def index():
    hooks.call("after_navigation")

    return render_template("index.html", plugins=get_plugins_list())


if __name__ == "__main__":
    app.run(debug=True)
