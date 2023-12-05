# -*- coding: utf8 -*-
# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : engine.py
# Create : 2017-08-19 18:18:46
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

import sublime
import sublime_plugin
import datetime
from datetime import datetime
import time
import threading
import traceback
import os
import shutil
import re
import webbrowser
import plistlib
import colorsys
import urllib.request
import json
import hashlib

from . import api
from . import persist

STVER = int(sublime.version())
DEFAULT_THEME = 'Default.sublime-theme'
DEFAULT_COLOR = 'Packages/Color Scheme - Default/Monokai.sublime-color-scheme'
ICONS_PACKAGE = 'A File Icon'
stopped   = False
lock_file = [
    ('Guna', 'Guna.sublime-settings'),
    ('Guna', 'themes', 'preset', 'Guna-dark.sublime-settings'),
    ('Guna', 'themes', 'preset', 'Guna-light.sublime-settings')
]
lock_file_path = []
for f in lock_file:
    path = os.path.join(*f)
    lock_file_path.append(path)
last_theme   = ''
last_color   = ''
last_bgclr   = ''
last_gopts   = ''
last_wigon   = ''
widget_index = 0
font_index   = -1
nok_cnt      = 0

def start():
    api.set_except()
    GunaMainThread.clean_gnis()
    check_gpu_window_buffer()
    observe_prefs()
    sublime.set_timeout_async(engine_reload, 0)
    wait_and_start()

def stop():
    global stopped
    stopped = True
    check_thread('prproc', stop=True)
    check_thread('fkproc', stop=True)
    check_thread('mnproc', stop=True)
    GunaMainThread.clean_gnis()
    GunaMainThread.clean_prfs()
    GunaMainThread.clean_gnc()
    GunaMainThread.clean_gnw()
    GunaMainThread.clean_gnd()
    GunaMainThread.clean_widget_other(True)
    restore_theme()

def observe_prefs(observer=None):
    global stopped
    if stopped:
        return
    prefs = sublime.load_settings("Preferences.sublime-settings")
    prefs.clear_on_change('Guna-prefs')
    prefs.add_on_change('Guna-prefs', observer or on_prefs_update)
    gunas = sublime.load_settings("Guna.sublime-settings")
    gunas.clear_on_change('Guna-gunas')
    gunas.add_on_change('Guna-gunas', observer or on_prefs_update)
    gunad = sublime.load_settings("Guna-dark.sublime-settings")
    gunad.clear_on_change('Guna-gunad')
    gunad.add_on_change('Guna-gunad', tweak_theme)
    gunal = sublime.load_settings("Guna-light.sublime-settings")
    gunal.clear_on_change('Guna-gunal')
    gunal.add_on_change('Guna-gunal', tweak_theme)

def tweak_theme():
    prefs, theme, is_guna = get_prefs()
    if is_guna:
        sublime.active_window().run_command('guna_tweak_theme')
    else:
        sublime.active_window().run_command('guna_tweak_widget')

def on_prefs_update():
    global stopped
    if stopped:
        return

    def prefs_reload():
        observe_prefs()
    observe_prefs(observer=prefs_reload)
    is_alive = check_thread('prproc', stop=False)
    if not is_alive:
        pthread = GunaPrefThread()
        pthread.setDaemon(True)
        pthread.start()

def engine_reload():
    observe_prefs(observer=on_prefs_update)
    tweak = False
    global last_theme, last_color, last_bgclr, last_gopts, last_wigon
    prefs, theme, is_guna = get_prefs()
    color = prefs.get('color_scheme', '')
    gunas = sublime.load_settings("Guna.sublime-settings")
    fgclr = gunas.get('guna_fgcolor', '#E5E0D3')
    bgclr = gunas.get('guna_bgcolor', '#161C23')
    csopt = gunas.get('guna_color_saturation', 100)
    cbopt = gunas.get('guna_color_brightness', 100)
    gdclr = gunas.get('guna_guide', '#20272E')
    agclr = gunas.get('guna_active_guide', '#AAFF9954')
    brclr = gunas.get('guna_brackets_color', '#FF0000')
    tgclr = gunas.get('guna_tags_color', '#FF5242')
    bropt = gunas.get('guna_brackets_options', 'foreground')
    tgopt = gunas.get('guna_tags_options', 'foreground')
    ttbar = gunas.get('title_bar_color', True)
    gopts = str(csopt) + str(cbopt) + fgclr + gdclr + agclr + brclr + tgclr + bropt + tgopt + str(ttbar)
    if theme != last_theme or color != last_color or bgclr != last_bgclr or gopts != last_gopts:
        last_color = color
        tweak = True
    gunas, widgt, wigon, is_clock = get_gunas('clock')
    if not is_guna and not wigon and last_wigon == 'False':
        if last_theme == 'Guna.sublime-theme':
            GunaMainThread.clean_gnis()
            GunaMainThread.clean_prfs()
            GunaMainThread.clean_gnc()
            GunaMainThread.clean_gnw()
            GunaMainThread.clean_gnd()
        last_theme = theme
        return
    if str(wigon) != last_wigon:
        last_wigon = str(wigon)
    if theme != last_theme:
        last_theme = theme
        GunaMainThread.clean_gnc()
        GunaMainThread.clean_gnw()
        GunaMainThread.clean_gnd()
        GunaMainThread.clean_widget_other(is_guna)
    GunaMainThread.init_prefs(prefs, gunas, is_guna, wigon)
    if is_guna and tweak:
        sublime.active_window().run_command('guna_tweak_theme')
    else:
        sublime.active_window().run_command('guna_tweak_widget')

def get_prefs():
    prefs   = sublime.load_settings("Preferences.sublime-settings")
    theme   = prefs.get('theme', '')
    is_guna = cmp_str(theme, 'Guna.sublime-theme')
    return prefs, theme, is_guna

def get_gunas(widget='clock'):
    gunas = sublime.load_settings("Guna.sublime-settings")
    widgt = gunas.get('sidebar_widget', [])
    wigon = gunas.get('sidebar_widget_on_other_theme', True)
    wigtf = True if widget in widgt else False
    return gunas, widgt, wigon, wigtf
vSicIYDw = os.path.getmtime

def get_style():
    aview = sublime.active_window().active_view()
    prefs = sublime.load_settings("Preferences.sublime-settings")
    cschm = prefs.get('color_scheme')
    viewc = '' if aview is None else aview.settings().get('color_scheme')
    if aview is None or cschm != viewc:
        view = sublime.active_window().new_file()
        style = view.style()
        sublime.active_window().focus_view(view)
        sublime.active_window().run_command('close_file')
        return style
    else:
        return aview.style()

def cmp_str(item, string):
    return (isinstance(item, str) and item == string)

def wait_and_start():
    is_alive = check_thread('fkproc', stop=False)
    if not is_alive:
        fthread = GunaForkThread()
        fthread.setDaemon(True)
        fthread.start()

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

def check_status(prefs=None, view=None):
    global stopped
    if stopped:
        return
    aviw = sublime.active_window().active_view()
    if aviw is None:
        return
    if view is None:
        view = aviw
    else:
        if view != aviw:
            return
    if prefs is None:
        prefs = sublime.load_settings("Preferences.sublime-settings")
    theme = prefs.get('theme', '')
    gunas = sublime.load_settings("Guna.sublime-settings")
    wigon = gunas.get('sidebar_widget_on_other_theme', True)
    if cmp_str(theme, 'Guna.sublime-theme') or wigon:
        if not view.settings().get('is_widget'):
            is_reado = prefs.get(persist.GNC_READ_ONLY, False)
            if view.is_read_only():
                if not is_reado:
                    prefs.set(persist.GNC_READ_ONLY, True)
            else:
                if is_reado:
                    prefs.set(persist.GNC_READ_ONLY, False)
            if view.is_read_only():
                prefs.set(persist.GNC_DIRTY, False)
            else:
                is_dirty = prefs.get(persist.GNC_DIRTY, False)
                if view.is_dirty() or view.is_scratch():
                    if not is_dirty:
                        prefs.set(persist.GNC_DIRTY, True)
                else:
                    if is_dirty:
                        prefs.set(persist.GNC_DIRTY, False)

def restore_theme():
    prefs = sublime.load_settings("Preferences.sublime-settings")
    prefs.set('color_scheme', DEFAULT_COLOR)
    prefs.set('theme', DEFAULT_THEME)
    sublime.save_settings("Preferences.sublime-settings")

def check_gpu_window_buffer():
    if sublime.platform() == 'osx':
        prefs = sublime.load_settings("Preferences.sublime-settings")
        gwbis = prefs.get('gpu_window_buffer', 'auto')
        if isinstance(gwbis, bool) and gwbis == False:
            pass
        else:
            prefs.set('gpu_window_buffer', False)
            sublime.message_dialog("GUNA MESSAGE :\n\nTo prevent flickering for OSX, 'gpu_window_buffer' is set as false.\nPlease, restart sublime text.\n\nIf you don't want this message, set 'gpu_window_buffer_false': false in Guna.sublime-settings")

def icons():
    pkgctrls = sublime.load_settings("Package Control.sublime-settings")
    if ICONS_PACKAGE in pkgctrls.get("installed_packages", []):
        return
    iconok = sublime.ok_cancel_dialog("GUNA MESSAGE :\n\nGuna recommends 'A File Icon' for sidebar icons. Do you want to install it?", "Install")
    if iconok:
        print("Installing `{}` ...".format(ICONS_PACKAGE))
        sublime.active_window().run_command("advanced_install_package", {"packages": ICONS_PACKAGE})
    return

def disp_error():
    print ('GUNA : ERROR ―――――――――――――――――――――――――――――――――――――――――――――――――――――――――')
    traceback.print_exc()
    print ('――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――――')
    api.GunaApi.alert_message(3, " GUNA : Error is occured. Please, see the trace-back message in Sublime console.", 10, 1)

def timenow():
    return datetime.now()

def ftimestamp(arg):
    return datetime.fromtimestamp(arg)

def maketime(arg1, arg2):
    return time.mktime(time.strptime(arg1, arg2))

class GunaPrefThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, name='prproc')
        self.quit = False

    def run(self):
        try:
            time.sleep(1)
            if not self.quit:
                engine_reload()
        except Exception:
            disp_error()

    def stop(self):
        self.quit = True

class GunaForkThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, name='fkproc')
        self.quit = False

    def run(self):
        while True:
            try:
                if self.quit:
                    break
                is_alive = check_thread('mnproc', stop=True)
                if is_alive:
                    time.sleep(1)
                else:
                    guna_thread = GunaMainThread()
                    guna_thread.setDaemon(True)
                    guna_thread.start()
                    break
            except Exception:
                disp_error()
                break

    def stop(self):
        self.quit = True

class GunaMainThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self, name='mnproc')
        self.quit = False
        self.tick = 0

    def run(self):
        while True:
            try:
                time.sleep(30)
                self.tick = 0 if self.tick == 1000 else (self.tick + 1)
                if self.quit:
                    break
                GunaMainThread.set_time()
                GunaMainThread.set_date()
                GunaMainThread.set_weather(self.tick)
            except Exception:
                disp_error()
                break

    def stop(self):
        self.quit = True

    def status(self):
        return not self.quit

    @staticmethod
    def clean_gnis():
        prefs = sublime.load_settings("Preferences.sublime-settings")
        change = False
        for k in persist.GUNA_GNIS:
            if prefs.has(k):
                change = True
                prefs.erase(k)
        if change:
            sublime.save_settings("Preferences.sublime-settings")

    @staticmethod
    def clean_prfs():
        prefs = sublime.load_settings("Preferences.sublime-settings")
        for k in persist.GUNA_PREF:
            if prefs.has(k):
                prefs.erase(k)

    @staticmethod
    def clean_widget_other(is_guna):
        try:
            if is_guna:
                tpath = os.path.join(sublime.packages_path(), 'zzz Guna Widget zzz')
                if os.path.exists(tpath):
                    shutil.rmtree(tpath)
            else:
                prefs = sublime.load_settings("Preferences.sublime-settings")
                theme = prefs.get('theme', '')
                tpath = os.path.join(sublime.packages_path(), 'zzz Guna Widget zzz/themes')
                for _dir in os.walk(tpath):
                    files = _dir[2]
                    for _file in files:
                        if _file != theme:
                            tfile = os.path.join(tpath, _file)
                            os.remove(tfile)
        except:
            pass

    @staticmethod
    def init_prefs(prefs, gunas, is_guna, wigon):
        current_sets = {}
        for k in persist.GUNA_PREF:
            if prefs.has(k):
                v = prefs.get(k)
                current_sets[k] = v
        change = False
        check_sets = {}
        if is_guna or wigon:
            sets = gunas.get('sidebar_widget', [])
            if len(sets) > 0:
                global widget_index
                widget_index = widget_index % len(sets)
                if sets[widget_index] == 'clock':
                    widget_type = 1
                    check_sets[persist.GNW_WIDGET_CLOCK] = True
                elif sets[widget_index] == 'date':
                    widget_type = 2
                    check_sets[persist.GNW_WIDGET_DATE] = True
                elif sets[widget_index] == 'weather':
                    widget_type = 3
                    check_sets[persist.GNW_WIDGET_WEATHER] = True
                else:
                    widget_type = 0
                    check_sets[persist.GNW_WIDGET_OFF] = True
            else:
                widget_type = 0
                check_sets[persist.GNW_WIDGET_OFF] = True
            GunaMainThread.set_bool(gunas, check_sets, 'hide_tab_close', persist.GNS_HIDE_TAB_CLOSE, False)
            GunaMainThread.set_bool(gunas, check_sets, 'hide_tab_dropdown', persist.GNS_HIDE_TAB_DROPDOWN, False)
            GunaMainThread.set_bool(gunas, check_sets, 'overlay_scroll_bars', persist.GNS_OVERLAY_SCROLL_BARS, False)
            GunaMainThread.set_bool(gunas, check_sets, 'scroll_bars_convex', persist.GNS_SCROLL_BARS_CONVEX, False)
            GunaMainThread.set_bool(gunas, check_sets, 'sidebar_selected_box', persist.GNS_SIDEBAR_BOX, False)
            GunaMainThread.set_bool(gunas, check_sets, 'sidebar_head', persist.GNS_SIDEBAR_HEAD, False)
            GunaMainThread.set_bool(gunas, check_sets, 'title_bar_color', persist.GNS_TITLE_BAR_COLOR, False)
            if gunas.get('sidebar_widget_on_other_theme', True):
                check_sets[persist.GNW_WIDGET_OTHER] = True
            for k in current_sets.keys():
                if k in check_sets:
                    if current_sets[k] != check_sets[k]:
                        prefs.set(k, check_sets[k])
                        change = True
                else:
                    prefs.erase(k)
                    change = True
            for k in check_sets.keys():
                if not k in current_sets:
                    prefs.set(k, check_sets[k])
                    change = True
            if widget_type == 1:
                GunaMainThread.set_time()
            if widget_type == 2:
                GunaMainThread.set_date()
            if widget_type == 3:
                GunaMainThread.set_weather()
        else:
            for k in persist.GUNA_PREF:
                if prefs.has(k):
                    prefs.erase(k)
                    change = True
        if change:
            sublime.save_settings("Preferences.sublime-settings")
        return

    @staticmethod
    def set_bool(gunas, pref_sets, gitem, pitem, default):
        sets = gunas.get(gitem, default)
        if sets != default:
            pref_sets[pitem] = sets

    @staticmethod
    def set_prfx(gunas, pref_sets, gitem, pitem, default):
        sets = gunas.get(gitem, default)
        pitem = pitem + sets.lower()
        if sets != default and any(pitem == s for s in persist.GUNA_PREF):
            pref_sets[pitem] = True

    @staticmethod
    def erase_prefs(prefs, key):
        if prefs.has(key):
            prefs.erase(key)

    @staticmethod
    def clean_gnc():
        prefs = sublime.load_settings("Preferences.sublime-settings")
        GunaMainThread.erase_prefs(prefs, persist.GNC_DIRTY)
        GunaMainThread.erase_prefs(prefs, persist.GNC_READ_ONLY)
        for x in range(0,24):
            kstr = "gnc_h{:02d}".format(x)
            GunaMainThread.erase_prefs(prefs, kstr)
        for w in range(0,7):
            for x in range(0,6):
                kstr = "gnc_w{:d}m1{:d}".format(w,x)
                GunaMainThread.erase_prefs(prefs, kstr)
        for x in range(0,10):
            kstr = "gnc_m0{:d}".format(x)
            GunaMainThread.erase_prefs(prefs, kstr)
        sublime.save_settings("Preferences.sublime-settings")
        if not stopped:
            sublime.set_timeout_async(GunaMainThread.set_time, 1000)

    @staticmethod
    def set_time():
        prefs, theme, is_guna  = get_prefs()
        gunas, widgt, wigon, is_clock = get_gunas('clock')
        if (not is_guna and not wigon) or not is_clock:
            return
        check_status(prefs=prefs, view=None)
        now   = timenow()
        if gunas.get('sidebar_widget_clock_mode', '24h') == '24h':
            hour = now.hour
        else:
            hour = 12 if (now.hour % 12) == 0 else (now.hour % 12)
        hrkey = GunaMainThread.get_hour(hour)
        m1key = GunaMainThread.get_wxmin1x(now.weekday(),now.minute)
        m0key = GunaMainThread.get_min0x(now.minute)
        if not prefs.has(hrkey):
            for x in range(0,24):
                kstr = "gnc_h{:02d}".format(x)
                GunaMainThread.erase_prefs(prefs, kstr)
            prefs.set(hrkey, True)
        if not prefs.has(m1key):
            for x in range(0, 7):
                for y in range(0, 6):
                    kstr = "gnc_w{:d}m1{:d}".format(x,y)
                    GunaMainThread.erase_prefs(prefs, kstr)
            prefs.set(m1key, True)
        if not prefs.has(m0key):
            for x in range(0, 10):
                kstr = "gnc_m0{:d}".format(x)
                GunaMainThread.erase_prefs(prefs, kstr)
            prefs.set(m0key, True)
        return

    @staticmethod
    def get_hour(hour):
        hstr = "gnc_h{:02d}".format(hour)
        return hstr

    @staticmethod
    def get_min1x(min):
        return ('gnc_m1' + str(min//10))

    @staticmethod
    def get_min0x(min):
        return ('gnc_m0' + str(min - 10 * (min//10)))

    @staticmethod
    def get_wxmin1x(wday, min):
        return ('gnc_w' + str(wday) + 'm1' + str(min//10))

    @staticmethod
    def clean_gnd():
        prefs = sublime.load_settings("Preferences.sublime-settings")
        GunaMainThread.erase_prefs(prefs, persist.GNC_DIRTY)
        GunaMainThread.erase_prefs(prefs, persist.GNC_READ_ONLY)
        for x in range(1,13):
            kstr = "gnd_m{:02d}".format(x)
            GunaMainThread.erase_prefs(prefs, kstr)
        for w in range(0,7):
            for x in range(0,4):
                kstr = "gnd_w{:d}d1{:d}".format(w,x)
                GunaMainThread.erase_prefs(prefs, kstr)
        for x in range(0,10):
            kstr = "gnd_d0{:d}".format(x)
            GunaMainThread.erase_prefs(prefs, kstr)
        sublime.save_settings("Preferences.sublime-settings")
        if not stopped:
            sublime.set_timeout_async(GunaMainThread.set_time, 1000)

    @staticmethod
    def set_date():
        prefs, theme, is_guna = get_prefs()
        gunas, widgt, wigon, is_date = get_gunas('date')
        if (not is_guna and not wigon) or not is_date:
            return
        check_status(prefs=prefs, view=None)
        now   = timenow()
        mnkey = GunaMainThread.get_month(now.month)
        d1key = GunaMainThread.get_wxday1x(now.weekday(),now.day)
        d0key = GunaMainThread.get_day0x(now.day)
        if not prefs.has(mnkey):
            for x in range(1,13):
                kstr = "gnd_m{:02d}".format(x)
                GunaMainThread.erase_prefs(prefs, kstr)
            prefs.set(mnkey, True)
        if not prefs.has(d1key):
            for x in range(0, 7):
                for y in range(0, 4):
                    kstr = "gnd_w{:d}d1{:d}".format(x,y)
                    GunaMainThread.erase_prefs(prefs, kstr)
            prefs.set(d1key, True)
        if not prefs.has(d0key):
            for x in range(0, 10):
                kstr = "gnd_d0{:d}".format(x)
                GunaMainThread.erase_prefs(prefs, kstr)
            prefs.set(d0key, True)
        return

    @staticmethod
    def get_month(month):
        mstr = "gnd_m{:02d}".format(month)
        return mstr

    @staticmethod
    def get_day0x(day):
        return ('gnd_d0' + str(day - 10 * (day//10)))

    @staticmethod
    def get_wxday1x(wday, day):
        return ('gnd_w' + str(wday) + 'd1' + str(day//10))

    @staticmethod
    def set_weather(tick=0):
        prefs, theme, is_guna = get_prefs()
        gunas, widgt, wigon, is_weather = get_gunas('weather')
        if (not is_guna and not wigon) or not is_weather:
            return
        witem = False
        for x in persist.GUNA_WEATHERS:
            kstr = 'gnw_0' + x
            if prefs.has(kstr):
                witem = True
        global nok_cnt
        if witem and tick % 20 != 0:
            return
        if not witem and nok_cnt > 5:
            return
        ok, w0icn, w3icn, w6icn = GunaMainThread.get_weather()
        if not ok:
            nok_cnt += 1
        else:
            nok_cnt  = 0
        if not prefs.has(w0icn):
            for x in persist.GUNA_WEATHERS:
                kstr = 'gnw_0' + x
                GunaMainThread.erase_prefs(prefs, kstr)
                pass
            if ok:
                prefs.set(w0icn, True)
        if not prefs.has(w3icn):
            for x in persist.GUNA_WEATHERS:
                kstr = 'gnw_3' + x
                GunaMainThread.erase_prefs(prefs, kstr)
                pass
            if ok:
                prefs.set(w3icn, True)
        if not prefs.has(w6icn):
            for x in persist.GUNA_WEATHERS:
                kstr = 'gnw_6' + x
                GunaMainThread.erase_prefs(prefs, kstr)
                pass
            if ok:
                prefs.set(w6icn, True)
        return

    @staticmethod
    def get_weather():
        fpath = os.path.join(sublime.cache_path(), 'Guna', 'cache')
        if not os.path.exists(fpath):
            os.makedirs(fpath)
        wpath = os.path.join(sublime.cache_path(), 'Guna', 'cache', '.weather')
        fpath = os.path.join(sublime.cache_path(), 'Guna', 'cache', '.forecast')
        gunas, widgt, wigon, is_weather = get_gunas('weather')
        if gunas.has('weather'):
            weast = gunas.get('weather')
            if 'appid' in weast:
                appid = str(weast['appid'])
            else:
                appid = ""
            if 'city_name' in weast:
                cname = str(weast['city_name']).lower()
            else:
                cname = ""
            if 'geographic' in weast:
                geogr = weast['geographic']
                if 'lat' in geogr:
                    golat = int(geogr.get('lat'))
                else:
                    golat = -1
                if 'lon' in geogr:
                    golon = int(geogr.get('lon'))
                else:
                    golon = -1
            else:
                geogr = None
                golat = -1
                golon = -1
            if 'proxy' in weast:
                proxy = weast['proxy']
            else:
                proxy = ""
        try:
            read_ok = False
            weathjs = {}
            fcastjs = {}
            if not os.path.exists(wpath) or not os.path.exists(fpath):
                GunaMainThread.update_weather(wpath, fpath, appid, cname, geogr, golat, golon, proxy)
                read_ok, weathjs, fcastjs = GunaMainThread.read_weather(wpath, fpath)
            else:
                read_ok, weathjs, fcastjs = GunaMainThread.read_weather(wpath, fpath)
                if read_ok:
                    nowdt = timenow()
                    weadt = ftimestamp(weathjs["dt"])
                    delta = nowdt - weadt
                    cityn = str(weathjs['name']).lower() + ',' + str(weathjs['sys']['country']).lower()
                    if delta.seconds > (30 * 60) or cname != cityn:
                        GunaMainThread.update_weather(wpath, fpath, appid, cname, geogr, golat, golon, proxy)
                        read_ok, weathjs, fcastjs = GunaMainThread.read_weather(wpath, fpath)
                else:
                    GunaMainThread.update_weather(wpath, fpath, appid, cname, geogr, golat, golon, proxy)
                    read_ok, weathjs, fcastjs = GunaMainThread.read_weather(wpath, fpath)
            if read_ok:
                weadt = ftimestamp(weathjs["dt"])
                forct = ftimestamp(fcastjs['list'][0]['dt'])
                delta = forct - weadt
                w0icn = 'gnw_0' + str(weathjs['weather'][0]['icon'])[:2]
                if delta.seconds < (90 * 60):
                    w3icn = 'gnw_3' + str(fcastjs['list'][1]['weather'][0]['icon'])[:2]
                    w6icn = 'gnw_6' + str(fcastjs['list'][2]['weather'][0]['icon'])[:2]
                else:
                    w3icn = 'gnw_3' + str(fcastjs['list'][0]['weather'][0]['icon'])[:2]
                    w6icn = 'gnw_6' + str(fcastjs['list'][1]['weather'][0]['icon'])[:2]
                return True, w0icn, w3icn, w6icn
            else:
                return False, 'gnw_0xx', 'gnw_3xx', 'gnw_6xx'
        except:
            disp_error()
            return False, 'gnw_0xx', 'gnw_3xx', 'gnw_6xx'

    @staticmethod
    def read_weather(wpath, fpath):
        read_ok = False
        weathjs = {}
        fcastjs = {}
        try:
            if os.path.exists(wpath):
                with open(wpath, 'r', encoding="utf8") as dfile:
                    weathjs = json.load(dfile)
            if os.path.exists(fpath):
                with open(fpath, 'r', encoding="utf8") as dfile:
                    fcastjs = json.load(dfile)
            if "dt" in weathjs and "list" in fcastjs:
                read_ok = True
        except:
            pass
        return read_ok, weathjs, fcastjs

    @staticmethod
    def update_weather(wpath, fpath, appid, cname, geogr, golat, golon, proxy):
        try:
            if appid != "" and (cname != "" or (geogr != None and golat != -1 and golon != -1)):
                if cname != "":
                    wlink = 'http://api.openweathermap.org/data/2.5/weather?q=' + cname + '&APPID=' + appid
                    flink = 'http://api.openweathermap.org/data/2.5/forecast?q=' + cname + '&APPID=' + appid
                else:
                    wlink = 'http://api.openweathermap.org/data/2.5/weather?lat=' + str(golat) + '&lon=' + str(golon) + '&APPID=' + appid
                    flink = 'http://api.openweathermap.org/data/2.5/forecast?lat=' + str(golat) + '&lon=' + str(golon) + '&APPID=' + appid
                urlrq = urllib.request.Request(wlink)
                if proxy != "":
                    urlrq.set_proxy(proxy, 'http')
                urlda = urllib.request.urlopen(urlrq)
                weath = urlda.read().decode('utf-8')
                wjson = json.loads(weath)
                if "dt" in wjson:
                    with open(wpath, 'w', newline="", encoding="utf8") as dfile:
                        json.dump(wjson, dfile)
                    urlrq = urllib.request.Request(flink)
                    if proxy != "":
                        urlrq.set_proxy(proxy, 'http')
                    urlda = urllib.request.urlopen(urlrq)
                    weath = urlda.read().decode('utf-8')
                    wjson = json.loads(weath)
                    with open(fpath, 'w', newline="", encoding="utf8") as dfile:
                        json.dump(wjson, dfile)
                else:
                    GunaMainThread.clean_weather_files(wpath, fpath)
            else:
                GunaMainThread.clean_weather_files(wpath, fpath)
        except:
            # GunaMainThread.clean_weather_files(wpath, fpath)
            # disp_error()
            pass
        return

    @staticmethod
    def clean_weather_files(wpath, fpath):
        if os.path.exists(wpath):
            os.remove(wpath)
        if os.path.exists(fpath):
            os.remove(fpath)

    @staticmethod
    def clean_gnw():
        prefs = sublime.load_settings("Preferences.sublime-settings")
        for x in persist.GUNA_WEATHERS:
            kstr = "gnw_0" + x
            GunaMainThread.erase_prefs(prefs, kstr)
            kstr = "gnw_3" + x
            GunaMainThread.erase_prefs(prefs, kstr)
            kstr = "gnw_6" + x
            GunaMainThread.erase_prefs(prefs, kstr)
        sublime.save_settings("Preferences.sublime-settings")
        if not stopped:
            sublime.set_timeout_async(GunaMainThread.set_weather, 1000)

    @staticmethod
    def switch_widget():
        prefs = sublime.load_settings("Preferences.sublime-settings")
        gunas = sublime.load_settings("Guna.sublime-settings")
        widgt = gunas.get('sidebar_widget', [])
        if len(widgt) > 0:
            global widget_index
            widget_index = (widget_index + 1) % len(widgt)
            GunaMainThread.erase_prefs(prefs, persist.GNW_WIDGET_CLOCK)
            GunaMainThread.erase_prefs(prefs, persist.GNW_WIDGET_DATE)
            GunaMainThread.erase_prefs(prefs, persist.GNW_WIDGET_WEATHER)
            if widgt[widget_index] == 'clock':
                prefs.set(persist.GNW_WIDGET_CLOCK, True)
            elif widgt[widget_index] == 'date':
                prefs.set(persist.GNW_WIDGET_DATE, True)
            elif widgt[widget_index] == 'weather':
                prefs.set(persist.GNW_WIDGET_WEATHER, True)
        return

    @staticmethod
    def switch_font(cmd):
        prefs = sublime.load_settings("Preferences.sublime-settings")
        gunas = sublime.load_settings("Guna.sublime-settings")
        fonts = gunas.get('font_switch', [])
        sface = cmd
        if cmd == 'up':
            updown = 0
        elif cmd == 'down':
            updown = 1
        else:
            updown = 2
        if len(fonts) > 0:
            global font_index
            if font_index < 0:
                font_index = 0
            if updown == 0 or updown == 1:
                fface = prefs.get("font_face", "system")
                for i, f in enumerate(fonts):
                    if f[0] == fface:
                        font_index = i
                        break
                font_index = (font_index - 1) if updown == 0 else (font_index + 1)
                font_index = font_index % len(fonts)
            else:
                for i, f in enumerate(fonts):
                    if f[0] == sface:
                        font_index = i
                        break
            prefs.set("font_face", fonts[font_index][0])
            prefs.set("font_size", fonts[font_index][1])
            sublime.save_settings("Preferences.sublime-settings")
            sublime.status_message(' Font : ' + fonts[font_index][0] + ' (' + str(fonts[font_index][1]) + ')')
        return

class GunaEventListener(sublime_plugin.EventListener):

    def on_new_async(self, view):
        check_status(prefs=None, view=view)

    def on_load_async(self, view):
        check_status(prefs=None, view=view)

    def on_modified_async(self, view):
        check_status(prefs=None, view=view)

    def on_activated_async(self, view):
        file_name = view.file_name()
        if isinstance(file_name, str):
            if any(file_name.endswith(p) for p in lock_file_path):
                view.set_read_only(True)
        check_status(prefs=None, view=view)

    def on_post_save_async(self, view):
        check_status(prefs=None, view=view)

    def on_close(self, view):
        global stopped
        file_name = view.file_name()
        if isinstance(file_name, str) and not stopped:
            if file_name.endswith("User/Preferences.sublime-settings") or file_name.endswith("User\\Preferences.sublime-settings"):
                GunaMainThread.clean_gnc()
                GunaMainThread.clean_gnw()
                GunaMainThread.clean_gnd()

class GunaSwitchWidget(sublime_plugin.WindowCommand):

    def run(self):
        GunaMainThread.switch_widget()

class GunaSetTheme(sublime_plugin.WindowCommand):

    def run(self):
        try:
            prefs, theme, is_guna = get_prefs()
            prefs = sublime.load_settings("Preferences.sublime-settings")
            prefs.set('theme', 'Guna.sublime-theme')
            prefs.set('color_scheme', 'Packages/Guna/themes/Guna.sublime-color-scheme')
            sublime.save_settings("Preferences.sublime-settings")
        except Exception:
            disp_error()

class GunaReadme(sublime_plugin.WindowCommand):

    def run(self):
        try:
            w = sublime.active_window()
            for v in w.views():
                if v.name() == "Guna - README":
                    v.close()
            view = sublime.active_window().new_file()
            view.set_name("Guna - README")
            view.settings().set("gutter", False)
            view.settings().set("line_numbers", False)
            html = str(sublime.load_resource("Packages/Guna/.guna/guna-readme.html"))
            view.add_phantom("guna-readme",
                             sublime.Region(0),
                             html,
                             sublime.LAYOUT_INLINE,
                             on_navigate=self.on_navigate
            )
            view.set_read_only(True)
            view.set_scratch(True)
        except Exception:
            disp_error()

    def on_navigate(self, href):
        try:
            webbrowser.open(href)
        except Exception:
            disp_error()

class GunaIssue(sublime_plugin.WindowCommand):

    def run(self):
        try:
            webbrowser.open_new_tab('https://github.com/poucotm/Guna/issues')
        except Exception:
            disp_error()

SC1OBJ = re.compile(r'(?P<front>.*?)#scale1\s+(?:((?P<el00>[\d]+)-(?P<el01>[\d]+))|(?P<el0>[\d\-]+))(?P<back>.*)')
SC2OBJ = re.compile(r'(?P<front>.*?)#scale2-(?P<eli>[\d]+)\s*\[(?P<el0>[\d]+)\s*,\s*(?P<el1>[\d]+)\](?P<back>.*)')
SC4OBJ = re.compile(r'(?P<front>.*?)#scale4-(?P<eli>[\d]+)\s*\[(?P<el0>[\d]+)\s*,\s*(?P<el1>[\d]+)\s*,\s*(?P<el2>[\d]+)\s*,\s*(?P<el3>[\d]+)\](?P<back>.*)')
SW2OBJ = re.compile(r'(?P<front>.*?)#switch-scale2-(?P<eli>[\d]+)\s*\[(?P<el0>[\d]+)\s*,\s*(?P<el1>[\d]+)\](?P<back>.*)')
CMGOBJ = re.compile(r'"content_margin"\s*:\s*\[\s*\d+\s*,\s*\d+\s*\]')
AFIOBJ = re.compile(r'"size"\s*:\s*\d+')
LSTPAT = ''

class GunaTweakTheme(sublime_plugin.WindowCommand):
    GUNA_COLORS = [
        'white', 'red', 'green', 'blue', 'yellow', 'orange', 'lBlue', 'rOrange', 'lOrange'
    ]

    def run(self):
        try:
            prefs, theme, is_guna = get_prefs()
            if not is_guna:
                return
            cschm = prefs.get('color_scheme')
            gunac = cmp_str(cschm, 'Packages/Guna/themes/Guna.sublime-color-scheme')
            gunas = sublime.load_settings("Guna.sublime-settings")
            ttbar = gunas.get('title_bar_color', True)
            if not gunac:
                global STVER
                if STVER >= 3150:
                    style = get_style()
                    bgclr = style.get('background')
                else:
                    cschm = prefs.get('color_scheme')
                    cstxt = str(sublime.load_resource(cschm))
                    treep = plistlib.readPlistFromBytes(cstxt.encode())
                    bgclr = treep['settings'][0]['settings']['background']
            else:
                fgclr = gunas.get('guna_fgcolor', '#E5E0D3')
                bgclr = gunas.get('guna_bgcolor', '#161C23')
                csopt = gunas.get('guna_color_saturation', 100)
                cbopt = gunas.get('guna_color_brightness', 100)
                gdclr = gunas.get('guna_guide', '#20272E')
                agclr = gunas.get('guna_active_guide', '#AAFF9954')
                brclr = gunas.get('guna_brackets_color', '#FF0000')
                tgclr = gunas.get('guna_tags_color', '#FF5242')
                bropt = gunas.get('guna_brackets_options', 'foreground')
                tgopt = gunas.get('guna_tags_options', 'foreground')
                gopts = str(csopt) + str(cbopt) + fgclr + gdclr + agclr + brclr + tgclr + bropt + tgopt + str(ttbar)
                global last_bgclr
                last_bgclr  = bgclr
                global last_gopts
                last_gopts = gopts
            ttxt = str(sublime.load_resource("Packages/Guna/.guna/guna.sublime-theme-templ"))
            wtxt = str(sublime.load_resource("Packages/Guna/.guna/widget-guna.sublime-color-scheme-templ"))
            if gunac:
                ctxt = str(sublime.load_resource("Packages/Guna/.guna/guna.sublime-color-scheme-templ"))
            cbase = self.conv_hex_color(bgclr)
            (h, s, v) = colorsys.rgb_to_hsv(cbase[0], cbase[1], cbase[2])
            if v >= 200:
                gunas = sublime.load_settings("Guna-light.sublime-settings")
            else:
                gunas = sublime.load_settings("Guna-dark.sublime-settings")
            if v >= 230:
                clst = [5, 4, 3, 2, 1]
                for t in clst:
                    srcs = '#base-color+{0}i'.format(t)
                    dest = '"color(var(--background) l(- {0}%))"'.format(t*2)
                    desw = 'color(var(bgcolor) l(- {0}%))'.format(t*2)
                    ttxt = ttxt.replace(srcs, dest)
                    wtxt = wtxt.replace(srcs, desw)
                    srcs = '#base-color-{0}i'.format(t)
                    dest = '"color(var(--background) l(+ {0}%))"'.format(t*2)
                    desw = 'color(var(bgcolor) l(+ {0}%))'.format(t*2)
                    ttxt = ttxt.replace(srcs, dest)
                    wtxt = wtxt.replace(srcs, desw)
                ttxt = ttxt.replace('#dark-', '//')
                ttxt = ttxt.replace('#light-', '')
            else:
                clst = [5, 4, 3, 2, 1]
                for t in clst:
                    srcs = '#base-color+{0}i'.format(t)
                    dest = '"color(var(--background) l(+ {0}%))"'.format(t*2)
                    desw = 'color(var(bgcolor) l(+ {0}%))'.format(t*2)
                    ttxt = ttxt.replace(srcs, dest)
                    wtxt = wtxt.replace(srcs, desw)
                    srcs = '#base-color-{0}i'.format(t)
                    dest = '"color(var(--background) l(- {0}%))"'.format(t*2)
                    desw = 'color(var(bgcolor) l(- {0}%))'.format(t*2)
                    ttxt = ttxt.replace(srcs, dest)
                    wtxt = wtxt.replace(srcs, desw)
                ttxt = ttxt.replace('#dark-', '')
                ttxt = ttxt.replace('#light-', '//')
            if ttbar:
                ttxt = ttxt.replace('#title-bar', '')
            else:
                ttxt = ttxt.replace('#title-bar', '//')
            wtxt = wtxt.replace('#base-color', bgclr)
            if gunac:
                ctxt  = ctxt.replace('#base-color', bgclr)
                ctxt  = ctxt.replace('#fore-color', fgclr)
                ctxt  = ctxt.replace('#guide-color', gdclr)
                ctxt  = ctxt.replace('#active-guide-color', agclr)
                ctxt  = ctxt.replace('#bracket-color', brclr)
                ctxt  = ctxt.replace('#tag-color', tgclr)
                if bropt in ['foreground', 'underline', 'stippled_underline', 'squiggly_underline']:
                    ctxt  = ctxt.replace('#bracket-option', bropt)
                if tgopt in ['foreground', 'underline', 'stippled_underline', 'squiggly_underline']:
                    ctxt  = ctxt.replace('#tag-option', tgopt)
                regx = '"(?P<name>[\\w]+)"\\s*:\\s*"#(?P<color>[\\w]+)"'
                objt = re.compile(regx)
                for mtch in objt.finditer(ctxt):
                    if mtch.group('name') in GunaTweakTheme.GUNA_COLORS:
                        otext = mtch.group()
                        cbase = self.conv_hex_color('#' + mtch.group('color'))
                        h, s, v = colorsys.rgb_to_hsv(cbase[0], cbase[1], cbase[2])
                        v = v * (float(cbopt) / 100.0)
                        v = 255 if v > 255 else v
                        s = s * (float(csopt) / 100.0)
                        s = 1.0 if s > 1.0 else s
                        r, g, b = colorsys.hsv_to_rgb(h, s, v)
                        hxclr = '#{:02X}{:02X}{:02X}'.format(int(r), int(g), int(b))
                        ntext = otext.replace('#' + mtch.group('color'), hxclr)
                        ctxt = ctxt.replace(otext, ntext)
            cbclr = gunas.get('clock.color', '#FFCC67')
            cbclr = str(self.conv_hex_color(cbclr))
            cdclr = gunas.get('clock.color.dirty', '#FF3377')
            cdclr = str(self.conv_hex_color(cdclr))
            crclr = gunas.get('clock.color.readonly', '#B4B4B4')
            crclr = str(self.conv_hex_color(crclr))
            caclr = gunas.get('clock.color.alert', '#FF1919')
            caclr = str(self.conv_hex_color(caclr))
            ciclr = gunas.get('clock.color.info', '#19FFFF')
            ciclr = str(self.conv_hex_color(ciclr))
            ttxt  = ttxt.replace('#clock-color-dirty', cdclr)
            ttxt  = ttxt.replace('#clock-color-readonly', crclr)
            ttxt  = ttxt.replace('#clock-color-alert', caclr)
            ttxt  = ttxt.replace('#clock-color-info', ciclr)
            ttxt  = ttxt.replace('#clock-color', cbclr)
            ibclr = gunas.get('icon.color', '#677A83')
            ibclr = str(self.conv_hex_color(ibclr))
            isclr = gunas.get('icon.color.selected', '#FFCC67')
            isclr = str(self.conv_hex_color(isclr))
            ipclr = gunas.get('icon.color.pressed', '#FF5500')
            ipclr = str(self.conv_hex_color(ipclr))
            ihclr = gunas.get('icon.color.hover', '#FF5500')
            ihclr = str(self.conv_hex_color(ihclr))
            ttxt  = ttxt.replace('#icon-color-selected', isclr)
            ttxt  = ttxt.replace('#icon-color-pressed', ipclr)
            ttxt  = ttxt.replace('#icon-color-hover', ihclr)
            ttxt  = ttxt.replace('#icon-color', ibclr)
            tbclr = gunas.get('tab_font.color', '#969696')
            tbclr = str(self.conv_hex_color(tbclr))
            tsclr = gunas.get('tab_font.color.selected', '#FFFFFF')
            tsclr = str(self.conv_hex_color(tsclr))
            thclr = gunas.get('tab_font.color.hover', '#FFCC67')
            thclr = str(self.conv_hex_color(thclr))
            tdclr = gunas.get('tab_font.color.dirty', '#F92672')
            tuclr = tdclr + '96'
            tdclr = str(self.conv_hex_color(tdclr))
            tuclr = str(self.conv_hex_color(tuclr))
            ttxt  = ttxt.replace('#tab-font-color-selected', tsclr)
            ttxt  = ttxt.replace('#tab-font-color-hover', thclr)
            ttxt  = ttxt.replace('#tab-font-color-dirty-unsel', tuclr)
            ttxt  = ttxt.replace('#tab-font-color-dirty', tdclr)
            ttxt  = ttxt.replace('#tab-font-color', tbclr)
            lbclr = gunas.get('label_font.color', '#969696')
            lbclr = str(self.conv_hex_color(lbclr))
            ttxt  = ttxt.replace('#label-font-color', lbclr)
            sbclr = gunas.get('sidebar_font.color', '#969696')
            sbclr = str(self.conv_hex_color(sbclr))
            ssclr = gunas.get('sidebar_font.color.selected', '#FFFFFF')
            ssclr = str(self.conv_hex_color(ssclr))
            shclr = gunas.get('sidebar_head.color', '#FFFFFF')
            shclr = str(self.conv_hex_color(shclr))
            ttxt  = ttxt.replace('#sidebar-font-color-selected', ssclr)
            ttxt  = ttxt.replace('#sidebar-font-color', sbclr)
            ttxt  = ttxt.replace('#sidebar-head-color', shclr)
            ubclr = gunas.get('status_bar_font.color', '#0095B3')
            ubclr = str(self.conv_hex_color(ubclr))
            ttxt  = ttxt.replace('#status_bar-font-color', ubclr)
            pnbcl = gunas.get('panel_font.color', '#A6988D')
            pnbcl = str(self.conv_hex_color(pnbcl))
            pbclr = gunas.get('panel_font.color.selected', '#FFEE99')
            pbclr = str(self.conv_hex_color(pbclr))
            pnmcl = gunas.get('panel_font.color.match', '#61DAF2')
            pnmcl = str(self.conv_hex_color(pnmcl))
            pmclr = gunas.get('panel_font.color.match.selected', '#FF5242')
            pmclr = str(self.conv_hex_color(pmclr))
            ttxt  = ttxt.replace('#panel-font-color-sel-match', pmclr)
            ttxt  = ttxt.replace('#panel-font-color-sel', pbclr)
            ttxt  = ttxt.replace('#panel-font-color-match', pnmcl)
            ttxt  = ttxt.replace('#panel-font-color', pnbcl)
            pnbcl = gunas.get('panel_path.color', '#A6988D')
            pnbcl = str(self.conv_hex_color(pnbcl))
            pbclr = gunas.get('panel_path.color.selected', '#FFEE99')
            pbclr = str(self.conv_hex_color(pbclr))
            pnmcl = gunas.get('panel_path.color.match', '#61DAF2')
            pnmcl = str(self.conv_hex_color(pnmcl))
            pmclr = gunas.get('panel_path.color.match.selected', '#FF5242')
            pmclr = str(self.conv_hex_color(pmclr))
            ttxt  = ttxt.replace('#panel-path-color-sel-match', pmclr)
            ttxt  = ttxt.replace('#panel-path-color-sel', pbclr)
            ttxt  = ttxt.replace('#panel-path-color-match', pnmcl)
            ttxt  = ttxt.replace('#panel-path-color', pnbcl)
            pwclr = gunas.get('input_font.color', '#FFCC99')
            wtxt  = wtxt.replace('#input-font-color', pwclr)
            rbclr = gunas.get('scroll_bars.color', '#297080')
            rbclr = str(self.conv_hex_color(rbclr))
            ttxt  = ttxt.replace('#scroll_bars-color', rbclr)
            tface = gunas.get('tab_font.face', 'Dejavu Sans')
            tface = '\"{0}\"'.format(tface)
            tbold = gunas.get('tab_font.bold', False)
            tbold = str(tbold).lower()
            tsize = gunas.get('tab_font.size', 13)
            tsize = str(tsize)
            ttxt  = ttxt.replace('#tab-font-face', tface)
            ttxt  = ttxt.replace('#tab-font-bold', tbold)
            ttxt  = ttxt.replace('#tab-font-size', tsize)
            lface = gunas.get('label_font.face', 'Dejavu Sans')
            lface = '\"{0}\"'.format(lface)
            lsize = gunas.get('label_font.size', 12)
            lsize = str(lsize)
            ttxt  = ttxt.replace('#label-font-face', lface)
            ttxt  = ttxt.replace('#label-font-size', lsize)
            sface = gunas.get('sidebar_font.face', 'Dejavu Sans')
            sface = '\"{0}\"'.format(sface)
            ssize = gunas.get('sidebar_font.size', 13)
            ssiz2 = ssize + 2
            ssize = str(ssize)
            ssiz2 = str(ssiz2)
            ssiz2 = str(ssiz2)
            ttxt  = ttxt.replace('#sidebar-font-face', sface)
            ttxt  = ttxt.replace('#sidebar-font-size+2', ssiz2)
            ttxt  = ttxt.replace('#sidebar-font-size', ssize)
            uface = gunas.get('status_bar_font.face', 'Roboto Condensed')
            uface = '\"{0}\"'.format(uface)
            usize = gunas.get('status_bar_font.size', 12)
            usize = str(usize)
            ttxt  = ttxt.replace('#status_bar-font-face', uface)
            ttxt  = ttxt.replace('#status_bar-font-size', usize)
            pface = gunas.get('panel_font.face', 'system')
            pface = '\"{0}\"'.format(pface)
            psize = gunas.get('panel_font.size', 14)
            psiz2 = psize - 2
            psize = str(psize)
            psiz2 = str(psiz2)
            ttxt  = ttxt.replace('#panel-font-face', pface)
            ttxt  = ttxt.replace('#panel-font-size-2', psiz2)
            ttxt  = ttxt.replace('#panel-font-size', psize)
            thopa = gunas.get('tab.opacity.hover', 0.6)
            topac = gunas.get('tab.opacity', 0.3)
            tuclh = gunas.get('tab.underscore.color.hover', '#AAFF99')
            tuclh = str(self.conv_hex_color(tuclh))
            tuclr = gunas.get('tab.underscore.color', '#FFCC67')
            tuclr = str(self.conv_hex_color(tuclr))
            ttxt  = ttxt.replace('#tab-opacity-hover', str(thopa))
            ttxt  = ttxt.replace('#tab-opacity', str(topac))
            ttxt  = ttxt.replace('#tab-underscore-color-hover', tuclh)
            ttxt  = ttxt.replace('#tab-underscore-color', tuclr)
            shadw = gunas.get('overlay_shadow', 4)
            sperc = '\"color(var(--background) l(- {0}%))\"'.format(shadw)
            ttxt  = ttxt.replace('#overlay-shadow', sperc)
            scale = gunas.get('scale', 1)
            switch_scale = gunas.get('switch_icon_scale', 1)
            stxt  = ''
            for line in ttxt.splitlines():
                stxt += self.scaling(line, scale, switch_scale) + '\n'
            nsize = str(int(8 * scale))
            fname = os.path.join(sublime.packages_path(), 'zzz A File Icon zzz','patches','general','multi','Guna.sublime-theme')
            if os.path.exists(fname):
                with open(fname, 'r', encoding='utf8') as f:
                    patch = str(f.read())
                cmtxt = '"content_margin": ['+nsize+', '+nsize+']'
                patch = CMGOBJ.sub(cmtxt, patch)
                with open(fname, 'w', newline='', encoding='utf8') as f:
                    f.write(patch)
            fname = os.path.join(sublime.packages_path(), 'User','A File Icon.sublime-settings')
            patch = ''
            if os.path.exists(fname):
                with open(fname, 'r', encoding='utf8') as f:
                    patch = str(f.read())
                sztxt = '"size": '+nsize
                patch = AFIOBJ.sub(sztxt, patch)
            else:
                patch = '{ "size": '+nsize+' }'
            global LSTPAT
            if LSTPAT != patch:
                LSTPAT = patch
                with open(fname, 'w', newline='', encoding='utf8') as f:
                    f.write(patch)
            WGSCL = [1, 1.5]
            wscal = gunas.get('scale', 1)
            diffl = [abs(wscal-x) for x in WGSCL]
            minix = diffl.index(min(diffl))
            wscal = WGSCL[minix]
            if wscal == 1:
                sclx = ''
                stxt = stxt.replace('#sscale-@1.0x', '')
                stxt = stxt.replace('#sscale-@1.5x', '//')
                stxt = stxt.replace('#sscale-@2.0x', '//')
            elif wscal == 1.5:
                sclx = '-s1.5'
                stxt = stxt.replace('#sscale-@1.0x', '//')
                stxt = stxt.replace('#sscale-@1.5x', '')
                stxt = stxt.replace('#sscale-@2.0x', '//')
            elif wscal == 2:
                sclx = '-s2.0'
                stxt = stxt.replace('#sscale-@1.0x', '//')
                stxt = stxt.replace('#sscale-@1.5x', '//')
                stxt = stxt.replace('#sscale-@2.0x', '')
            stxt  = stxt.replace('-sscale', sclx)
            WGSCL = [1, 1.33]
            wscal = gunas.get('widget_scale', 1)
            diffl = [abs(wscal-x) for x in WGSCL]
            minix = diffl.index(min(diffl))
            wscal = WGSCL[minix]
            if wscal == 1:
                sclx = ''
                sclm = '[120, 40, 0, 0]'
                stxt = stxt.replace('#wscale-@1.0x', '')
                stxt = stxt.replace('#wscale-@1.3x', '//')
                stxt = stxt.replace('#wscale-@1.8x', '//')
            elif wscal == 1.33:
                sclx = '-s1.3'
                sclm = '[160, 52, 0, 0]'
                stxt = stxt.replace('#wscale-@1.0x', '//')
                stxt = stxt.replace('#wscale-@1.3x', '')
                stxt = stxt.replace('#wscale-@1.8x', '//')
            elif wscal == 1.8:
                sclx = '-s1.8'
                sclm = '[210, 72, 0, 0]'
                stxt = stxt.replace('#wscale-@1.0x', '//')
                stxt = stxt.replace('#wscale-@1.3x', '//')
                stxt = stxt.replace('#wscale-@1.8x', '')
            stxt  = stxt.replace('-wscale', sclx)
            wgtxt = ''
            for i in range(0,24):
                wgtxt += '\t{{ "class": "sidebar_container", "layer1.inner_margin": {}, "settings" : ["gnc_h{:02d}",   "gnwidg1"], "layer1.texture": "Guna/assets/simple/sidebar/clock/clock_h{:02d}{}.png", "layer1.opacity": 1 }},\n'.format(sclm, i, i, sclx)
            wgtxt += '\n'
            for w in range(0,7):
                for m in range(10,16):
                    wgtxt += '\t{{ "class": "sidebar_container", "layer2.inner_margin": {}, "settings" : ["gnc_w{:d}m{:02d}", "gnwidg1"], "layer2.texture": "Guna/assets/simple/sidebar/clock/clock_w{:d}m{:02d}{}.png", "layer2.opacity": 1 }},\n'.format(sclm, w, m, w, m, sclx)
            wgtxt += '\n'
            for i in range(0,10):
                wgtxt += '\t{{ "class": "sidebar_container", "layer3.inner_margin": {}, "settings" : ["gnc_m{:02d}",   "gnwidg1"], "layer3.texture": "Guna/assets/simple/sidebar/clock/clock_m{:02d}{}.png", "layer3.opacity": 1 }},\n'.format(sclm, i, i, sclx)
            stxt  = stxt.replace('#widget-clock', wgtxt)
            wgtxt = ''
            for i in range(1,13):
                wgtxt += '\t{{ "class": "sidebar_container", "layer1.inner_margin": {}, "settings" : ["gnd_m{:02d}",   "gnwidg2"], "layer1.texture": "Guna/assets/simple/sidebar/clock/clock_dm{:02d}{}.png", "layer1.opacity": 1 }},\n'.format(sclm, i, i, sclx)
            wgtxt += '\n'
            for w in range(0,7):
                for m in range(10,14):
                    wgtxt += '\t{{ "class": "sidebar_container", "layer2.inner_margin": {}, "settings" : ["gnd_w{:d}d{:02d}", "gnwidg2"], "layer2.texture": "Guna/assets/simple/sidebar/clock/clock_w{:d}m{:02d}{}.png", "layer2.opacity": 1 }},\n'.format(sclm, w, m, w, m, sclx)
            wgtxt += '\n'
            for i in range(0,10):
                wgtxt += '\t{{ "class": "sidebar_container", "layer3.inner_margin": {}, "settings" : ["gnd_d{:02d}",   "gnwidg2"], "layer3.texture": "Guna/assets/simple/sidebar/clock/clock_m{:02d}{}.png", "layer3.opacity": 1 }},\n'.format(sclm, i, i, sclx)
            stxt  = stxt.replace('#widget-date', wgtxt)
            wgtxt = ''
            ixwea = [1,2,3,4,9,10,11,13,50]
            iwwea = [1,2,3,3,9,10,11,13,50]
            for i in range(0,9):
                wgtxt += '\t{{ "class": "sidebar_container", "layer1.inner_margin": {}, "settings" : ["gnw_{:03d}",   "gnwidg3"], "layer1.texture": "Guna/assets/simple/sidebar/weather/w{:03d}{}.png", "layer1.opacity": 1 }},\n'.format(sclm, ixwea[i], iwwea[i], sclx)
            wgtxt += '\n'
            ixwea = [x+300 for x in ixwea]
            iwwea = [x+300 for x in iwwea]
            for i in range(0,9):
                wgtxt += '\t{{ "class": "sidebar_container", "layer2.inner_margin": {}, "settings" : ["gnw_{:03d}",   "gnwidg3"], "layer2.texture": "Guna/assets/simple/sidebar/weather/w{:03d}{}.png", "layer2.opacity": 1 }},\n'.format(sclm, ixwea[i], iwwea[i], sclx)
            wgtxt += '\n'
            ixwea = [x+300 for x in ixwea]
            iwwea = [x+300 for x in iwwea]
            for i in range(0,9):
                wgtxt += '\t{{ "class": "sidebar_container", "layer3.inner_margin": {}, "settings" : ["gnw_{:03d}",   "gnwidg3"], "layer3.texture": "Guna/assets/simple/sidebar/weather/w{:03d}{}.png", "layer3.opacity": 1 }},\n'.format(sclm, ixwea[i], iwwea[i], sclx)
            stxt  = stxt.replace('#widget-weather', wgtxt)
            fname = os.path.join(sublime.packages_path(), 'Guna/themes/Guna.sublime-theme')
            with open(fname, "w", newline="", encoding='utf8') as f:
                f.write(stxt)
            fname = os.path.join(sublime.packages_path(), 'Guna/widgets/Widget - Guna.sublime-color-scheme')
            with open(fname, "w", newline="", encoding='utf8') as f:
                f.write(wtxt)
            if gunac:
                fname = os.path.join(sublime.packages_path(), 'Guna/themes/Guna.sublime-color-scheme')
                with open(fname, "w", newline="", encoding='utf8') as f:
                    f.write(ctxt)
        except Exception:
            disp_error()
        return

    def sat_color(self, c):
        return 255 if c > 255 else c

    def conv_hex_color(self, hc):
        if len(hc) == 7:
            return [int(hc[1:3], 16), int(hc[3:5], 16), int(hc[5:7], 16)]
        elif len(hc) == 9:
            return [int(hc[1:3], 16), int(hc[3:5], 16), int(hc[5:7], 16), int(hc[7:9], 16)]
        else:
            raise
            return

    def scaling(self, txt, scale, switch_scale):
        mch = SC1OBJ.match(txt)
        if mch:
            if mch.group('el00') and mch.group('el01'):
                els = str( int((int(mch.group('el00'))-int(mch.group('el01'))) * scale + int(mch.group('el01'))) )
                return (mch.group('front') + els + mch.group('back'))
            else:
                els = str( int(int(mch.group('el0')) * scale) )
                return (mch.group('front') + els + mch.group('back'))
        else:
            mch = SC2OBJ.match(txt)
            ele = []
            if mch:
                eli = mch.group('eli')
                ele.append(mch.group('el0'))
                ele.append(mch.group('el1'))
                for e in eli:
                    i = int(e)
                    ele[i] = str( int(int(ele[i]) * scale) )
                els = '['+', '.join(ele)+']'
                return (mch.group('front') + els + mch.group('back'))
            else:
                mch = SC4OBJ.match(txt)
                if mch:
                    eli = mch.group('eli')
                    ele.append(mch.group('el0'))
                    ele.append(mch.group('el1'))
                    ele.append(mch.group('el2'))
                    ele.append(mch.group('el3'))
                    for e in eli:
                        i = int(e)
                        ele[i] = str( int(int(ele[i]) * scale) )
                    els = '['+', '.join(ele)+']'
                    return (mch.group('front') + els + mch.group('back'))
                else:
                    mch = SW2OBJ.match(txt)
                    ele = []
                    if mch:
                        eli = mch.group('eli')
                        ele.append(mch.group('el0'))
                        ele.append(mch.group('el1'))
                        for e in eli:
                            i = int(e)
                            ele[i] = str( int(int(ele[i]) * scale * switch_scale) )
                        els = '['+', '.join(ele)+']'
                        return (mch.group('front') + els + mch.group('back'))
                    return txt

class GunaTweakWidget(sublime_plugin.WindowCommand):

    def run(self):
        try:
            prefs, theme, is_guna = get_prefs()
            gunas, widgt, wigon, is_clock = get_gunas('clock')
            if not wigon or theme == 'Guna.sublime-theme':
                return
            global STVER
            if STVER >= 3150:
                style = get_style()
                bgclr = style.get('background')
            else:
                cschm = prefs.get('color_scheme')
                cstxt = str(sublime.load_resource(cschm))
                treep = plistlib.readPlistFromBytes(cstxt.encode())
                bgclr = treep['settings'][0]['settings']['background']
            cbase = self.conv_hex_color(bgclr)
            (h, s, v) = colorsys.rgb_to_hsv(cbase[0], cbase[1], cbase[2])
            if v >= 200:
                gunas = sublime.load_settings("Guna-light.sublime-settings")
            else:
                gunas = sublime.load_settings("Guna-dark.sublime-settings")
            stxt = str(sublime.load_resource("Packages/Guna/.guna/guna-widget.sublime-theme-templ"))
            cbclr = gunas.get('clock.color', '#FFCC67')
            cbclr = str(self.conv_hex_color(cbclr))
            cdclr = gunas.get('clock.color.dirty', '#FF3377')
            cdclr = str(self.conv_hex_color(cdclr))
            crclr = gunas.get('clock.color.readonly', '#B4B4B4')
            crclr = str(self.conv_hex_color(crclr))
            caclr = gunas.get('clock.color.alert', '#FF1919')
            caclr = str(self.conv_hex_color(caclr))
            ciclr = gunas.get('clock.color.info', '#19FFFF')
            ciclr = str(self.conv_hex_color(ciclr))
            stxt  = stxt.replace('#clock-color-dirty', cdclr)
            stxt  = stxt.replace('#clock-color-readonly', crclr)
            stxt  = stxt.replace('#clock-color-alert', caclr)
            stxt  = stxt.replace('#clock-color-info', ciclr)
            stxt  = stxt.replace('#clock-color', cbclr)
            WGSCL = [1, 1.33]
            wscal = gunas.get('widget_scale', 1)
            diffl = [abs(wscal-x) for x in WGSCL]
            minix = diffl.index(min(diffl))
            wscal = WGSCL[minix]
            if wscal == 1:
                sclx = ''
                sclm = '[120, 40, 0, 0]'
                stxt = stxt.replace('#wscale-@1.0x', '')
                stxt = stxt.replace('#wscale-@1.3x', '//')
                stxt = stxt.replace('#wscale-@1.8x', '//')
            elif wscal == 1.33:
                sclx = '-s1.3'
                sclm = '[160, 52, 0, 0]'
                stxt = stxt.replace('#wscale-@1.0x', '//')
                stxt = stxt.replace('#wscale-@1.3x', '')
                stxt = stxt.replace('#wscale-@1.8x', '//')
            elif wscal == 1.8:
                sclx = '-s1.8'
                sclm = '[210, 72, 0, 0]'
                stxt = stxt.replace('#wscale-@1.0x', '//')
                stxt = stxt.replace('#wscale-@1.3x', '//')
                stxt = stxt.replace('#wscale-@1.8x', '')
            stxt  = stxt.replace('-wscale', sclx)
            wgtxt = ''
            for i in range(0,24):
                wgtxt += '\t{{ "class": "sidebar_container", "layer1.inner_margin": {}, "settings" : ["gnc_h{:02d}",   "gnwidg1"], "layer1.texture": "Guna/assets/simple/sidebar/clock/clock_h{:02d}{}.png", "layer1.opacity": 1 }},\n'.format(sclm, i, i, sclx)
            wgtxt += '\n'
            for w in range(0,7):
                for m in range(10,16):
                    wgtxt += '\t{{ "class": "sidebar_container", "layer2.inner_margin": {}, "settings" : ["gnc_w{:d}m{:02d}", "gnwidg1"], "layer2.texture": "Guna/assets/simple/sidebar/clock/clock_w{:d}m{:02d}{}.png", "layer2.opacity": 1 }},\n'.format(sclm, w, m, w, m, sclx)
            wgtxt += '\n'
            for i in range(0,10):
                wgtxt += '\t{{ "class": "sidebar_container", "layer3.inner_margin": {}, "settings" : ["gnc_m{:02d}",   "gnwidg1"], "layer3.texture": "Guna/assets/simple/sidebar/clock/clock_m{:02d}{}.png", "layer3.opacity": 1 }},\n'.format(sclm, i, i, sclx)
            stxt  = stxt.replace('#widget-clock', wgtxt)
            wgtxt = ''
            for i in range(1,13):
                wgtxt += '\t{{ "class": "sidebar_container", "layer1.inner_margin": {}, "settings" : ["gnd_m{:02d}",   "gnwidg2"], "layer1.texture": "Guna/assets/simple/sidebar/clock/clock_dm{:02d}{}.png", "layer1.opacity": 1 }},\n'.format(sclm, i, i, sclx)
            wgtxt += '\n'
            for w in range(0,7):
                for m in range(10,14):
                    wgtxt += '\t{{ "class": "sidebar_container", "layer2.inner_margin": {}, "settings" : ["gnd_w{:d}d{:02d}", "gnwidg2"], "layer2.texture": "Guna/assets/simple/sidebar/clock/clock_w{:d}m{:02d}{}.png", "layer2.opacity": 1 }},\n'.format(sclm, w, m, w, m, sclx)
            wgtxt += '\n'
            for i in range(0,10):
                wgtxt += '\t{{ "class": "sidebar_container", "layer3.inner_margin": {}, "settings" : ["gnd_d{:02d}",   "gnwidg2"], "layer3.texture": "Guna/assets/simple/sidebar/clock/clock_m{:02d}{}.png", "layer3.opacity": 1 }},\n'.format(sclm, i, i, sclx)
            stxt  = stxt.replace('#widget-date', wgtxt)
            wgtxt = ''
            ixwea = [1,2,3,4,9,10,11,13,50];
            iwwea = [1,2,3,3,9,10,11,13,50];
            for i in range(0,9):
                wgtxt += '\t{{ "class": "sidebar_container", "layer1.inner_margin": {}, "settings" : ["gnw_{:03d}",   "gnwidg3"], "layer1.texture": "Guna/assets/simple/sidebar/weather/w{:03d}{}.png", "layer1.opacity": 1 }},\n'.format(sclm, ixwea[i], iwwea[i], sclx)
            wgtxt += '\n'
            ixwea = [x+300 for x in ixwea]
            iwwea = [x+300 for x in iwwea]
            for i in range(0,9):
                wgtxt += '\t{{ "class": "sidebar_container", "layer2.inner_margin": {}, "settings" : ["gnw_{:03d}",   "gnwidg3"], "layer2.texture": "Guna/assets/simple/sidebar/weather/w{:03d}{}.png", "layer2.opacity": 1 }},\n'.format(sclm, ixwea[i], iwwea[i], sclx)
            wgtxt += '\n'
            ixwea = [x+300 for x in ixwea]
            iwwea = [x+300 for x in iwwea]
            for i in range(0,9):
                wgtxt += '\t{{ "class": "sidebar_container", "layer3.inner_margin": {}, "settings" : ["gnw_{:03d}",   "gnwidg3"], "layer3.texture": "Guna/assets/simple/sidebar/weather/w{:03d}{}.png", "layer3.opacity": 1 }},\n'.format(sclm, ixwea[i], iwwea[i], sclx)
            stxt  = stxt.replace('#widget-weather', wgtxt)
            tpath = os.path.join(sublime.packages_path(), 'zzz Guna Widget zzz')
            if not os.path.exists(tpath):
                os.mkdir(tpath)
                tpath = os.path.join(tpath, 'themes')
                os.mkdir(tpath)
            fname = os.path.join(sublime.packages_path(), 'zzz Guna Widget zzz/themes', theme)
            with open(fname, "w", newline="", encoding='utf8') as f:
                f.write(stxt)
        except Exception:
            disp_error()
        return

    def conv_hex_color(self, hc):
        if len(hc) == 7:
            return [int(hc[1:3], 16), int(hc[3:5], 16), int(hc[5:7], 16)]
        elif len(hc) == 9:
            return [int(hc[1:3], 16), int(hc[3:5], 16), int(hc[5:7], 16), int(hc[7:9], 16)]
        else:
            raise
            return

FTYOBJ = re.compile(r'(?P<name>file_type_\w+[^\.\@]*)\.png')

class GunaUpscaleIcon(sublime_plugin.WindowCommand):

    def run(self):
        try:
            afidir = os.path.join(sublime.packages_path(), 'zzz A File Icon zzz','patches','general','multi')
            if os.path.exists(afidir):
                for file in os.listdir(afidir):
                    mch = FTYOBJ.match(file)
                    if mch:
                        file = mch.group('name')
                        file = os.path.join(afidir, file)
                        if os.path.exists(file+'_1x.png'):
                            break
                        if os.path.exists(file+'.png'):
                            os.rename(file+'.png', file+'_1x.png')
                        if os.path.exists(file+'@2x.png'):
                            os.rename(file+'@2x.png', file+'_2x.png')
                        if os.path.exists(file+'@3x.png'):
                            os.rename(file+'@3x.png', file+'_3x.png')
                        if os.path.exists(file+'_3x.png'):
                            shutil.copy(file+'_3x.png', file+'.png')
                        elif os.path.exists(file+'_2x.png'):
                            shutil.copy(file+'_2x.png', file+'.png')
                        elif os.path.exists(file+'_1x.png'):
                            shutil.copy(file+'_1x.png', file+'.png')
        except Exception:
            disp_error()
        return

class GunaSwitchFont(sublime_plugin.WindowCommand):

    def run(self, **args):
        GunaMainThread.switch_font(args['cmd'])

class GunaAuxCmds(sublime_plugin.WindowCommand):

    def run(self, **args):
        if args['cmd'] == 'show_sidebar':
            api.GunaApi.show_sidebar()
        elif args['cmd'] == 'hide_sidebar':
            api.GunaApi.hide_sidebar()
