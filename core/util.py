# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Author : yongchan jeon (Kris) poucotm@gmail.com
# File   : util.py
# Create : 2023-04-11 23:27:21
# Editor : sublime text3, tab size (4)
# -----------------------------------------------------------------------------

import sublime
import sublime_plugin
import re
import colorsys

class GunaColorEdit(sublime_plugin.TextCommand):
    FLTOBJ = re.compile(r'[^0-9a-fA-F]')

    def run(self, edit, **args):
        acmd = args['cmd']
        selr = self.view.sel()[0]
        stxt = self.view.substr(selr)
        srch = self.FLTOBJ.search(stxt)
        if srch or len(stxt) != 6:
            return
        ccode = self.conv_hex_color(stxt)
        (h, s, v) = colorsys.rgb_to_hsv(ccode[0], ccode[1], ccode[2])
        if acmd == 'sat_up':
            s = s + 0.01
            s = 1.0 if s > 1.0 else s
        elif acmd == 'sat_down':
            s = s - 0.01
            s = 0.0 if s < 0.0 else s
        elif acmd == 'hue_up':
            h = h + 0.01
            h = 1.0 if h > 1.0 else h
        elif acmd == 'hue_down':
            h = h - 0.01
            h = 0.0 if h < 0.0 else h
        elif acmd == 'bri_up':
            v = v + 1
            v = 255 if v > 255 else v
        elif acmd == 'bri_down':
            v = v - 5
            v = 0 if v < 0 else v
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        ccode = '{:02x}{:02x}{:02x}'.format(int(r), int(g), int(b))
        self.view.replace(edit, selr, ccode)

    def conv_hex_color(self, hc):
        if len(hc) == 6:
            return [int(hc[0:2], 16), int(hc[2:4], 16), int(hc[4:6], 16)]
        elif len(hc) == 8:
            return [int(hc[0:2], 16), int(hc[2:4], 16), int(hc[4:6], 16), int(hc[6:8], 16)]
        else:
            return
