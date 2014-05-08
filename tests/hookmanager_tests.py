import unittest

from flask.ext.plugins import HookManager, Hook


class HookManagerTests(unittest.TestCase):

    def setUp(self):
        self.hooks = HookManager()
        self.hooks.new('foo', Hook())

    def callback(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def test_no_hooks(self):
        hooks = HookManager()
        self.assertEqual(hooks.hooks, {})

    def test_adds_new_hook(self):
        self.assert_(self.hooks.hooks['foo'])

    def test_adds_callback(self):
        self.hooks.add('foo', self.callback)
        self.assertEqual(self.hooks.hooks['foo'].callbacks, [self.callback])

    def test_removes_callback(self):
        cb_id = self.hooks.add('foo', self.callback)
        self.hooks.remove('foo', cb_id)
        self.assertEqual(self.hooks.hooks['foo'].callbacks, [])

    def test_calls_callbacks(self):
        self.hooks.add('foo', self.callback)
        self.hooks.call('foo', 'bar', kwarg='foobar')
        self.assertEqual(self.args, ('bar',))
        self.assertEqual(self.kwargs, {'kwarg': 'foobar'})

    def test_call_returns_value_of_callbacks(self):
        self.hooks.new('bar', Hook())
        self.hooks.add('bar', lambda data: data + 1)
        self.assertEqual(self.hooks.call('bar', 1), 2)

    def test_call_hook_without_callbacks(self):
        self.hooks.new('foobar', Hook())
        self.assertEqual(self.hooks.call('foobar'), "")
