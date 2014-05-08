import unittest

from flask.ext.plugins import Hook


class HookTests(unittest.TestCase):

    def setUp(self):
        self.hook = Hook()

    def callback(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def test_has_no_callbacks_by_default(self):
        self.assertEqual(self.hook.callbacks, [])

    def test_adds_callback(self):
        self.hook.add(self.callback)
        self.assertEqual(self.hook.callbacks, [self.callback])

    def test_adds_callback_only_once(self):
        self.hook.add(self.callback)
        self.hook.add(self.callback)
        self.assertEqual(self.hook.callbacks, [self.callback])

    def test_calls_callback(self):
        self.hook.add(self.callback)
        self.hook.call('bar', kwarg='foobar')
        self.assertEqual(self.args, ('bar',))
        self.assertEqual(self.kwargs, {'kwarg': 'foobar'})

    def test_removes_callback(self):
        callback = self.hook.add(self.callback)
        self.hook.remove(callback)
        self.assertEqual(self.hook.callbacks, [])
