from flask.ext.plugins import Plugin


__plugin__ = "TestTwoPlugin"


class TestTwoPlugin(Plugin):
    name = "Test Two"
    description = "Test Two description"
    author = "test2"
    license = "BSD"
    version = "0.1"
