# -*- coding: utf8 -*-
# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : api.py
# Create : 2017-08-23 00:38:01
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

import sublime
import sublime_plugin
import sys
import time
import datetime
import threading
import traceback

from . import persist

def check_thread(name, stop=False):
    is_alive = False
    for th in threading.enumerate():
        if th.name == name:
            is_alive = True
            if stop:
                th.stop()
            else:
                break
    return is_alive

def set_except():
    sys.excepthook = guna_except

def guna_except(exctype, value, tb):
    GunaApi.alert_message(3, " Uncaughted error is occured. Please, see the trace-back message in Sublime console.", 10, 1)
    sys.__excepthook__(exctype, value, tb)

class GunaApi():
    ALERT_CLOCK        = 1
    ALERT_STATUS_LABEL = 2
    ALERT_STATUS_BG    = 4
    INFO_CLOCK         = 8
    INFO_STATUS_LABEL  = 16
    FLICKER            = 1

    @staticmethod
    def alert_message(flag=0, message='', timeout=4, action=0):
        if flag != 0 and message != '' and timeout >= 1:
            GunaApi.alert(flag, True)
            check_thread('GunaAlertThread', stop=True)
            athread = GunaAlertThread(message, timeout, action, alert=True)
            athread.setDaemon(True)
            athread.start()

    @staticmethod
    def alert(flag=0, onoff=False):
        if flag & GunaApi.ALERT_CLOCK:
            GunaApi.set_prefs(persist.GNI_ALERT_CLOCK, onoff)
        if flag & GunaApi.ALERT_STATUS_LABEL:
            GunaApi.set_prefs(persist.GNI_ALERT_STATUS_LABEL, onoff)
        if flag & GunaApi.ALERT_STATUS_BG:
            GunaApi.set_prefs(persist.GNI_ALERT_STATUS_BG, onoff)

    @staticmethod
    def info_message(flag=0, message='', timeout=4, action=0):
        if flag != 0 and message != '' and timeout >= 1:
            GunaApi.info(flag, True)
            check_thread('GunaAlertThread', stop=True)
            athread = GunaAlertThread(message, timeout, action, alert=False)
            athread.setDaemon(True)
            athread.start()

    @staticmethod
    def info(flag=0, onoff=False):
        if flag & GunaApi.INFO_CLOCK:
            GunaApi.set_prefs(persist.GNI_INFO_CLOCK, onoff)
        if flag & GunaApi.INFO_STATUS_LABEL:
            GunaApi.set_prefs(persist.GNI_INFO_STATUS_LABEL, onoff)

    @staticmethod
    def set_prefs(item, onoff):
        prefs = sublime.load_settings("Preferences.sublime-settings")
        sets  = prefs.get(item, False)
        if prefs.has(item):
            if sets != onoff:
                if onoff:
                    prefs.set(item, True)
                else:
                    prefs.erase(item)
            pass
        else:
            prefs.set(item, onoff)

    @staticmethod
    def hide_sidebar():
        if sublime.active_window().is_sidebar_visible():
            sublime.active_window().run_command('toggle_side_bar')

    @staticmethod
    def show_sidebar():
        if not sublime.active_window().is_sidebar_visible():
            sublime.active_window().run_command('toggle_side_bar')

class GunaAlertThread(threading.Thread):

    def __init__(self, message, timeout, action, alert=True):
        threading.Thread.__init__(self, name='GunaAlertThread')
        self.message = message
        self.timeout = timeout
        self.action  = action
        self.alert   = alert
        self.quit    = False

    def run(self):
        while self.timeout > 0:
            if self.quit:
                break
            if self.action == GunaApi.FLICKER:
                sublime.status_message(self.message)
                time.sleep(0.4)
                sublime.status_message(" ")
                time.sleep(0.1)
            else:
                sublime.status_message(self.message)
                time.sleep(0.5)
            self.timeout = self.timeout - 1
        sublime.status_message("")
        if self.alert:
            GunaApi.alert(7, False)
        else:
            GunaApi.info(24, False)

    def stop(self):
        self.quit = True
