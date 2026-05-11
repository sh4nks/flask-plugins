import os

from flask_plugins import Plugin


def test_info_file(app):
    path = os.path.join(app.root_path, "plugins/test1")
    plugin = Plugin(path)

    assert plugin.name == "Test One"


def test_license_text(app):
    path = os.path.join(app.root_path, "plugins/test1")
    plugin = Plugin(path=path)

    assert plugin.license_text is not None


def test_no_license_text(app):
    path = os.path.join(app.root_path, "plugins/test2")
    plugin = Plugin(path=path)

    assert plugin.license_text is None
