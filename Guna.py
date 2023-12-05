# -*- coding: utf8 -*-
# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : Guna.py
# Create : 2017-08-31 22:09:10
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

import sublime, sublime_plugin
import sys, imp
import traceback

##  sub-modules  ______________________________________________

try:
    # reload
    mods = ['Guna.core.persist', 'Guna.core.api', 'Guna.core.engine']
    for mod in mods:
        if any(mod == m for m in list(sys.modules)):
            imp.reload(sys.modules[mod])
    # import
    from .core import persist
    from .core import api
    from .core.api import GunaApi
    from .core import engine
    from .core.engine import (GunaEventListener, GunaSwitchWidget, GunaSetTheme, GunaTweakTheme, GunaTweakWidget, GunaReadme,
        GunaIssue, GunaUpscaleIcon, GunaSwitchFont, GunaAuxCmds)
    from .core.util import (GunaColorEdit)
    import_ok = True
except Exception:
    print ('GUNA : ERROR ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――')
    traceback.print_exc()
    print ('――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――')
    import_ok = False

# package control
try:
    from package_control import events
    package_control_installed = True
except Exception:
    package_control_installed = False

##  plugin_loaded  ____________________________________________

def plugin_loaded():
    # import
    if not import_ok:
        sublime.status_message("* GUNA : Error in importing sub-modules. Please, see the trace-back message in Sublime console")
        return

    if package_control_installed and (events.install('Guna') or events.post_upgrade('Guna')):
        def installed():
            # automatically set theme
            sublime.active_window().run_command('guna_set_theme')
            # reload for settings
            engine.engine_reload()
            # engine start
            engine.start()
            # show `Read Me` @ first
            if events.install('Guna'):
                sublime.active_window().run_command('guna_readme')
                sublime.set_timeout_async(engine.icons(), 5000)
            # show sidebar (as default)
            sublime.active_window().run_command("guna_aux_cmds", {"cmd": "show_sidebar"})

        sublime.set_timeout_async(installed, 1000)
    else:
        # engine start
        engine.start()
    return

##  plugin_unloaded  __________________________________________

def plugin_unloaded():
    # engine stop
    if package_control_installed:
        if events.remove('Guna') or events.pre_upgrade('Guna'):
            engine.stop()
    return
