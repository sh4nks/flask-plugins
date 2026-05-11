Changelog
=========

Here you can see the full list of changes between each Flask-Plugins release.

Version 2.0.0
-------------

Released on May 11th, 2026

- Import `Markup` from `MarkupSafe` instead of `Jinja2`.
- Declare missing `MarkupSafe` and `Werkzeug` dependencies.
- Modernize project setup and switch to `uv`.
- Drop support for `Python < 3.10`.
- Drop support for `Flask < 2`.
- Use `pytest` for the tests.


Version 1.6.1
-------------

Released on January 26th, 2016

- Do not call ``Plugin.setup()`` method in ``Plugin.enable()``.

Version 1.6.0
-------------

Released on January 26th, 2016

- Documentation improvements
- Adds `enable` and `disable` methods for plugins
- BREAKING: The ``get_plugins_list()`` function got renamed to
  ``get_enabled_plugins()``.

Previous Versions
-----------------

Prior to 1.6.0, no proper changelog was kept.
