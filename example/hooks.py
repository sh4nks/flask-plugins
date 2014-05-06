from flask.ext.plugins import HookManager

# create a hookmanager instance which holds all your hooks
hooks = HookManager()

# create two new hooks which can than be used in your plugins
hooks.new("after_navigation")
hooks.new("tmpl_before_content")  # The "tmpl" prefix marks a template hook.
