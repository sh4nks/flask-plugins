from flask_plugins import Plugin


__plugin__ = "TestThreePlugin"


class TestThreePlugin(Plugin):
    name = "Test Three"
    description = "Test Three description"
    author = "test1"
    license = "BSD"
    version = "1.0"
