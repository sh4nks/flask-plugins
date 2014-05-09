from flask import flash, Blueprint, render_template, render_template_string
from example.app import AppPlugin
from example.hooks import hooks

__plugin__ = "HelloWorld"
__version__ = "1.0.0"


def hello_world():
    flash("Hello World from {} Plugin".format(__plugin__), "success")


def hello_world2():
    flash("Hello World 2 from {} Plugin".format(__plugin__), "success")


def inject_hello_world():
    return "<h1>Hello World Injected</h1>"


def inject_hello_world2():
    return "<h1>Hello World 2 Injected</h1>"


def inject_navigation_link():
    return render_template_string(
        """
            <li><a href="{{ url_for('hello.index') }}">Hello</a></li>
        """)


hello = Blueprint("hello", __name__, template_folder="templates")


@hello.route("/")
def index():
    return render_template("hello.html")


class HelloWorld(AppPlugin):

    name = "Hello World Plugin"

    description = ("This plugin gives a quick insight on how you can write "
                   "plugins with Flask-Plugins.")

    author = "sh4nks"

    license = "BSD License. See LICENSE file for more information."

    version = __version__

    def setup(self):
        self.register_blueprint(hello, url_prefix="/hello")

    def enable(self):
        hooks.add("after_navigation", hello_world)
        hooks.add("after_navigation", hello_world2)

        hooks.add("tmpl_before_content", inject_hello_world)
        hooks.add("tmpl_before_content", inject_hello_world2)

        hooks.add("tmpl_navigation_last", inject_navigation_link)

    def disable(self):
        # there is no way to unregister blueprints
        # you need to restart your application to unregister the blueprint
        hooks.remove("after_navigation", hello_world)
        hooks.remove("after_navigation", hello_world2)

        hooks.remove("tmpl_before_content", inject_hello_world)
        hooks.remove("tmpl_before_content", inject_hello_world2)

        hooks.remove("tmpl_navigation_last", inject_navigation_link)

    def install(self):
        pass

    def uninstall(self):
        pass
