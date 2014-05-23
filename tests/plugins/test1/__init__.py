from flask.ext.plugins import Plugin


__plugin__ = "TestOnePlugin"


class TestOnePlugin(Plugin):
    name = "Test One"
    description = "Test One description"
    author = "test1"
    license = "BSD"
    version = "1.0"

    setup_called = False
    install_called = False
    uninstall_called = False

    def setup(self):
        self.setup_called = True

    def install(self):
        self.install_called = True

    def uninstall(self):
        self.uninstall_called = True
