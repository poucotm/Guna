# -*- coding: utf8 -*-
# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : Guna.py
# Create : 2017-08-31 22:09:10
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

#`protect

import sublime, sublime_plugin
import sys, imp
import datetime
import traceback

##  sub-modules  ______________________________________________

try:
    # reload
    mods = ['Guna.core.persist', 'Guna.core.api', 'Guna.core.engine']
    for mod in list(sys.modules):
        if any(mod == m for m in mods):
            imp.reload(sys.modules[mod])
    # import
    from .core import persist
    from .core import api
    from .core.api import GunaApi
    from .core import engine
    from .core.engine import (GunaEventListener, GunaToggleWidget, GunaSetTheme, GunaTweakTheme, GunaToggleFullScreen, GunaReadme)
    import_ok = True
except Exception:
    print ('GUNA : ERROR ________________________________________________')
    traceback.print_exc()
    print ('=============================================================')
    import_ok = False

# check reload time
tchk = datetime.datetime.now()

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

    # check reload time btw. Guna.py and sub-modules
    tdt_eng = (tchk - engine.tchk).total_seconds()
    tdt_api = (tchk - api.tchk).total_seconds()
    tdt_per = (tchk - persist.tchk).total_seconds()
    if tdt_eng > 10 or tdt_api > 10 or tdt_per > 10:
        GunaApi.alert_message(3, " GUNA : Error in reloading sub-modules, Please, restart sublime text", 15, 1)
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
            # sublime.active_window().run_command('guna_readme')

        sublime.set_timeout_async(installed, 1000)
    else:
        # engine start
        engine.start()


##  plugin_unloaded  __________________________________________

def plugin_unloaded():

    # engine stop
    if package_control_installed:
        if events.remove('Guna') or events.pre_upgrade('Guna'):
            engine.stop()
    pass


#`endprotect
