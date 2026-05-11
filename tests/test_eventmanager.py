from markupsafe import Markup

from flask_plugins import connect_event
from flask_plugins import emit_event
from flask_plugins import EventManager
from flask_plugins import iter_listeners
from tests.test_pluginmanager import PluginManager


def cb():
    return "Fred"


def cb_before():
    pass


def test_event_manager_init_with_plugin_manager(app):
    plugin_manager = PluginManager(app)
    assert isinstance(plugin_manager._event_manager, EventManager)


def test_event_manager_standalone():
    event_manager = EventManager()
    assert isinstance(event_manager, EventManager)


def test_event_manager_connect():
    event_manager = EventManager()

    # Connect callbacks in specific order
    event_manager.connect("test-event", cb)  # index 1 (default)
    event_manager.connect("test-event", cb_before, "before")  # index 0
    event_manager.connect("test-event", cb, "after")  # index 2

    events = list(event_manager.iter("test-event"))
    assert events[0] == cb_before
    assert events[2] == cb


def test_event_manager_iter():
    event_manager = EventManager()

    assert len(list(event_manager.iter("test-event"))) == 0

    event_manager.connect("test-event", cb)
    assert len(list(event_manager.iter("test-event"))) == 1


def test_event_manager_remove():
    event_manager = EventManager()

    event_manager.connect("test-event", cb)
    assert len(list(event_manager.iter("test-event"))) == 1

    # Test removing non-existent event or callback
    event_manager.remove("wrong-event", cb)
    assert len(list(event_manager.iter("test-event"))) == 1

    event_manager.remove("test-event", cb_before)
    assert len(list(event_manager.iter("test-event"))) == 1

    # Test actual removal
    event_manager.remove("test-event", cb)
    assert len(list(event_manager.iter("test-event"))) == 0


def test_event_manager_template_emit():
    event_manager = EventManager()
    event_manager.connect("test-event", cb)
    assert isinstance(event_manager.template_emit("test-event"), Markup)


def test_helper_methods(app):
    # Testing the context-bound helper functions
    PluginManager(app)
    with app.test_request_context():
        connect_event("test-event", cb)
        events = list(iter_listeners("test-event"))
        emit_result = emit_event("test-event")

    assert len(events) == 1
    assert emit_result == ["Fred"]
