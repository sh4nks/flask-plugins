from flask import flash
from flask.ext.plugins import Plugin
from hooks import hooks

__plugin__ = "HelloWorld"
__version__ = "1.0.0"


def hello_world():
    flash("Hello World from {} Plugin".format(__plugin__), "success")


def inject_hello_world():
    return "<h1>Hello World Injected</h1>"


class HelloWorld(Plugin):

    name = "Hello World Plugin"

    description = ("This plugin gives a quick insight on how you can write "
                   "plugins with Flask-Plugins.")

    author = "sh4nks"

    license = "BSD License. See LICENSE file for more information."

    version = __version__

    def enable(self):
        hooks.add("after_navigation", hello_world)
        hooks.add("tmpl_before_content", inject_hello_world)

    def disable(self):
        hooks.remove("after_navigation", hello_world)
        hooks.remove("tmpl_before_content", inject_hello_world)

    def install(self):
        pass

    def uninstall(self):
        pass
