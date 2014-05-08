from flask.ext.plugins import Plugin

__plugin__ = "WrongPluginClass"


class TestWrongPlugin(Plugin):
    name = "Test Wrong"
    description = "Test Wrong description"
    author = "test1"
    license = "BSD"
    version = "1.0"

    def enable(self):  # pragma: no cover
        pass

    def disable(self):  # pragma: no cover
        pass

    def install(self):  # pragma: no cover
        pass

    def uninstall(self):  # pragma: no cover
        pass
