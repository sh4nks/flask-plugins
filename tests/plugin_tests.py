import os
import unittest

from flask import Flask
from flask_plugins import Plugin


class PluginTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True

    def test_info_file(self):
        path = os.path.join(self.app.root_path, "plugins/test1")
        plugin = Plugin(path)
        self.assertEquals(plugin.name, "Test One")

    def test_license_text(self):
        path = os.path.join(self.app.root_path, "plugins/test1")
        plugin = Plugin(path=path)
        self.assertIsNotNone(plugin.license_text)

    def test_no_license_text(self):
        path = os.path.join(self.app.root_path, "plugins/test2")
        plugin = Plugin(path=path)
        self.assertIsNone(plugin.license_text)
