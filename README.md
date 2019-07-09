[![Image of Guna][S1]][S1]

[![Package Control](https://packagecontrol.herokuapp.com/downloads/Guna.svg?style=round-square)](https://packagecontrol.io/packages/Guna)
[![PayPal](https://img.shields.io/badge/paypal-donate-blue.svg)][PM]

Guna is most innovative theme for sublime text 3. It supports various functions : conspicuous widgets (clock, weather) on sidebar, manually or adaptively tweakable theme colors, controlling status bar label by its own api.

### Theme Activation

Simply, run __*Guna*__ in __*command palette*__ (*cmd/ctrl+shift+p*). In case that other color-scheme is selected on adaptive mode, it reverts to Guna's original color-scheme. I recommend that you select __*View > Side Bar > Hide Open Files*__ for better view. When Guna removed, it automatically restores theme and color-scheme as the last before activating Guna.

### Fonts

Guna uses [__Dejavu Sans__][L1] as default font for UI and [Roboto Condensed][L2] is used only for status bar. But you can change them in the theme-tweak settings as you want. The editor font is [Meslo][L5] in screenshots above. For __Sublime Text 3 (3143)__ on Windows, in order to apply *Roboto Condensed*, you may have to add __*"theme_font_options": "gdi"*__ in Preference.sublime-settings.

### Widgets

__Clock__ : The color of clock expresses the status of active view.

![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-normal.png) : Normal state  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-dirty.png) : Dirty or scrach state  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-reado.png) : Read only state  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-alert.png) : Alert state (only controlled by API)  

__Weather__ : The weather widget is added (from v1.4.0). The widget uses [https://openweathermap.org](https://openweathermap.org) for weather information and you can access after getting your own [__AppID__](http://openweathermap.org/appid). After getting it, fill out weather settings in [__Guna.sublime-settings__][L6]. The 1st icon means current weather, the 2nd icon means forecast in 3 hours, the 3rd icon means forecast in 6 hours. Normally, it will be updated every half an hour.

![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-weather.png)



### Tweak Theme

__Manual__ mode : you can tweak fonts / colors as you want by changing [__Guna.sublime-settings__][L6]. After changing, run __*Guna : Tweak Theme*__ in __*command palette*__ (*cmd/ctrl+shift+p*) to apply your settings.

__Adaptive__ mode : Guna automatically tweaks theme colors to match selected other color-scheme. Basically, by matching background color, Guna can be combined with other color- schemes, like Monokai, Mariana, Ayu, ... Some examples are below. You need to restart once for the input panel change. In order to change font face or size in adaptive mode, simply restart sublime text after changing values in [__Guna.sublime-settings__][L6].

__*Adaptive Mode Testing Shot*__

[![Image of Guna][S5]][S5]

### API

You can control Guna's screen through Guna's APIs.
Currently, there are two functions for displaying alert situation.
If you want to see the example, simply type __*raise*__ in Sublime console.

<sup>(example - status bar label)</sup>  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-alert-0.png)

Please, refer to [__Guna's API__][L10]

### File Type Icons

Guna doesn't have it's own file type icons except for Verilog/Systemverilog.
In screenshots above, [A File Icon][L7] is used, and recommended.

### Donate

[![Doate Image](https://raw.githubusercontent.com/poucotm/Links/master/image/PayPal/donate-paypal.png)][PM]  
Thank you for donating. It is helpful to continue to improve the plug-in.

### Credits

- Icons designed by [Freepik](http://www.freepik.com/), [Dave Gandy](https://www.flaticon.com/authors/dave-gandy), [Madebyoliver](https://www.flaticon.com/authors/madebyoliver), [Gregor Cresnar](https://www.flaticon.com/authors/gregor-cresnar), [Smartline](https://www.flaticon.com/authors/smartline), [Vectors Market](https://www.flaticon.com/authors/vectors-market), [Alfredo Hernandez](https://www.alfredocreates.com/) from [www.flaticon.com](https://www.flaticon.com/) is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/)

### License

Guna is licensed under a [Creative Commons Attribution-NonCommercial 4.0 International License](https://creativecommons.org/licenses/by-nc/4.0/).

[S1]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-screenshot.png "enlarge"
[S4]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-screenshot-4.png "enlarge"
[S5]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-adaptive.gif "enlarge"
[L1]:https://dejavu-fonts.github.io/ "Dejavu Sans"
[L2]:https://fonts.google.com/specimen/Roboto "Roboto Family"
[L3]:https://fonts.google.com/specimen/Source+Sans+Pro "Source Sans Pro"
[L4]:https://fonts.google.com/specimen/Open+Sans "Open Sans"
[L5]:https://github.com/andreberg/Meslo-Font "Meslo"
[L6]:https://github.com/poucotm/Guna/blob/master/Guna.sublime-settings "Guna Settings"
[L7]:https://packagecontrol.io/packages/A%20File%20Icon "A File Icon"
[L8]:https://packagecontrol.io/packages/SublimeLinter "SublimeLinter"
[L9]:https://github.com/poucotm/Guna/blob/master/themes/preset/theme-settings.md
[L10]:https://github.com/poucotm/Guna/blob/master/README-API.md "Guna API"
[PP]:https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=89YVNDSC7DZHQ "PayPal"
[PM]:https://www.paypal.me/poucotm/1.0 "PayPal"
