import unittest

from flask.ext.plugins import Plugin


class PluginTests(unittest.TestCase):
    def setUp(self):
        self.plugin = Plugin()

    def test_name_is_none(self):
        self.assertEqual(self.plugin.name, None)

    def test_author_is_empty_string(self):
        self.assertEquals(self.plugin.author, "")

    def test_license_is_empty_string(self):
        self.assertEquals(self.plugin.license, "")

    def test_description_is_empty_string(self):
        self.assertEqual(self.plugin.description, "")

    def test_version_is_zeroes(self):
        self.assertEqual(self.plugin.version, '0.0.0')

    def test_enable_raises_exception(self):
        self.assertRaises(Exception, self.plugin.enable)

    def test_disable_raises_exception(self):
        self.assertRaises(Exception, self.plugin.disable)

    def test_install_raises_exception(self):
        self.assertRaises(Exception, self.plugin.install)

    def test_uninstall_raises_exception(self):
        self.assertRaises(Exception, self.plugin.uninstall)
