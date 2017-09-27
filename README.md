[![Image of Guna][S1]][S1]
[![Image of Guna][S2]][S2]

[![Package Control](https://packagecontrol.herokuapp.com/downloads/Guna.svg?style=round-square)](https://packagecontrol.io/packages/Guna)
[![PayPal](https://img.shields.io/badge/paypal-donate-blue.svg)][PM]

### Fonts

Guna uses [__Dejavu Sans__][L1] as default font for UI and [Roboto Condensed][L2] is used only for status bar. But you can change them in user settings among 5 fonts - [Dejavu Sans][L1], [Source Sans Pro][L3], [Open Sans][L4], [Roboto][L2], [Roboto Condensed][L2]. The editor font is [Meslo][L5] in screenshots above. For __Sublime Text 3 (3143)__ on Windows, in order to apply *Roboto Condensed*, you may have to add __*"theme_font_options": "gdi"*__ in Preference.sublime-settings.

### Theme Activation

Simply, run __*Guna*__ in __*command palette*__ (*cmd/ctrl+shift+p*). You don't need to edit __*theme*__ and __*color_scheme*__ directly in settings. I recommend that you select __*View > Side Bar > Hide Open Files*__ for better view. When Guna removed, it automatically restores theme and color scheme as the last before activating Guna. Guna supports [SublimeLinter][L8] not to override color-scheme.

### Settings

__DO NOT__ directly edit __*Preferences.sublime-settings*__. Use __*User/Guna.sublime-settings*__ by selecting __*Preferences > Package Settings > Guna > settings*__ menu. That is more comfortable. It will take effect in a second. There is no need to restart sublime text. Various options are ready to control UI like show/hide clock, colors, fonts, etc. Please, refer to [__Guna.sublime-settings__][L6]

### Clock Color

The color of clock expresses the status of active view.

![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-normal.png) : Normal state  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-dirty.png) : Dirty or scrach state  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-reado.png) : Read only state  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-alert.png) : Alert state (only controlled by API)

### Full Screen On Start

__*ctrl+f11*__(Windows/Linux), __*cmd+ctrl+f11*__(OSX) are full screen toggle keys on full screen start mode. You can turn on that mode in __*Guna.sublime-settings*__. The menu bar will be hidden in full screen mode and shown in normal mode. I recommend that you simply override original full screen toggle key as __*guna_toggle_full_screen*__. It acts as original when you turn off that mode.

### Key Map

__*f5*__(Windows/Linux), __*alt+f5*__(OSX) are assigned for refresh folder list in side bar.

### API

You can control Guna's screen through Guna's APIs. 
Currently, there are two functions for displaying alert situation. 
If you want to see the example, simply type __*raise*__ in Sublime console.

<sup>(example - status bar label)</sup>  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-alert-0.png)

<sup>(example - status bar background)</sup>  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-alert-1.png)

```python
# API import

from Guna.core.api import GunaApi

# API functions

GunaApi.alert(flag=0, onoff=False):
    """
    Makes the clock, status bar red for alarming

    flag = GunaApi.ALERT_CLOCK | GunaApi.ALRT_STATUS_LABEL | GunaApi.ALERT_STATUS_BG
    """

GunaApi.alert_message(flag=0, message='', timeout=4, action=0):
    """
    Makes red with a status message in a timeout(seconds).
    Within a timeout, a new message request will be ignored (will be replaced as a queue).

    action = GunaApi.FLICKER
    """
```


### Environment

Mainly designed and developed at **Sublime Text 3 (3126)** on Windows7 with non-high dpi display. Operation is not guranteed at lower versions. Occasionally, tested on OSX / Linux, the views are not exaclty same.

### File Type Icons

Guna doesn't have it's own file type icons except for Verilog/Systemverilog.
In screenshots above, [A File Icon][L7] is used, and recommended.

### Donate

[![Doate Image](https://raw.githubusercontent.com/poucotm/Links/master/image/PayPal/donate-paypal.png)][PM]  
Thank you for donating. It is helpful to continue to improve the plug-in.

### Credits

- Icons designed by [Freepik](http://www.freepik.com/), [Dave Gandy](https://www.flaticon.com/authors/dave-gandy), [Madebyoliver](https://www.flaticon.com/authors/madebyoliver), [Gregor Cresnar](https://www.flaticon.com/authors/gregor-cresnar), [Smartline](https://www.flaticon.com/authors/smartline), [Vectors Market](https://www.flaticon.com/authors/vectors-market) from [www.flaticon.com](https://www.flaticon.com/) is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/)

### License

Guna is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

[S1]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-screenshot-1.png "enlarge"
[S2]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-screenshot-2.png "enlarge"
[L1]:https://dejavu-fonts.github.io/ "Dejavu Sans"
[L2]:https://fonts.google.com/specimen/Roboto "Roboto Family"
[L3]:https://fonts.google.com/specimen/Source+Sans+Pro "Source Sans Pro"
[L4]:https://fonts.google.com/specimen/Open+Sans "Open Sans"
[L5]:https://github.com/andreberg/Meslo-Font "Meslo"
[L6]:https://github.com/poucotm/Guna/blob/master/Guna.sublime-settings "Guna Settings"
[L7]:https://packagecontrol.io/packages/A%20File%20Icon "A File Icon"
[L8]:https://packagecontrol.io/packages/SublimeLinter "SublimeLinter"
[PP]:https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=89YVNDSC7DZHQ "PayPal"
[PM]:https://www.paypal.me/poucotm/2.5 "PayPal"
