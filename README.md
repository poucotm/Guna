[![Image of Guna][S1]][S1]

[![Package Control](https://img.shields.io/packagecontrol/dt/Guna?logo=github&color=FF1919)][GUNA]
[![PayPal](https://img.shields.io/badge/paypal-donate-blue.svg)][PM]

Guna is an innovative theme for Sublime Text that offers a variety of features to enhance your coding experience. It includes prominent widgets such as a clock, weather updates, and date display on the sidebar. The theme colors are customizable, either manually or adaptively, allowing you to tweak them to your preference. Additionally, Guna supports font switching and provides an API to control the status bar label.

### Activating the Theme

To activate Guna, open the command palette by pressing <code>Cmd</code>/<code>Ctrl</code> + <code>Shift</code> + <code>P</code>, then type and select "Guna." If another color scheme has been selected in adaptive mode, it will revert to Guna's original color scheme. For an optimal view, it's recommended to navigate to <code>View</code> > <code>Side Bar</code> and select <code>Hide Open Files</code>. Upon removal of Guna, the theme and color scheme will automatically restore to their previous settings before Guna was activated.

### Fonts

By default, Guna uses [Dejavu Sans][L1] for the user interface and [Roboto Condensed][L2] specifically for the status bar. However, you can change these fonts in the theme-tweak settings according to your preferences. In the provided screenshots, the editor font used is Menlo, specifically the [Meslo][L5] variant.

### Widgets

__Clock__ / __Date__ : The clock's color indicates the status of the active view:

![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-normal.png) : Normal state  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-dirty.png) : Dirty or scratch state  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-reado.png) : Read-only state  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-status-alert.png) : Alert state (only controlled by API)  

__Weather__ : Introduced in version 1.4.0, the weather widget utilizes data from [Open Weather Map](https://openweathermap.org). To access this feature, obtain your own [AppID](http://openweathermap.org/appid) from Open Weather Map and configure the weather settings in [Guna.sublime-settings][L6]. The widget displays the current weather (1st icon) and forecasts for the next 3 and 6 hours (the 2nd, 3rd icon), updating every 30 minutes.

![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-weather.png)

__✹ Widgets can be viewed on other themes__

![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-widget-ayu.png)

### Adaptive Theme

Guna automatically adjusts its theme colors to match the selected color scheme by aligning the background color. This allows seamless integration with various color schemes like Monokai, Mariana, Ayu, and others. For easy customization of theme colors and fonts, navigate to <code>Preferences</code> > <code>Package Settings</code> > <code>Guna</code> > <code>Dark (Light) theme settings</code>.

__*Adaptive Theme Testing Shot*__

[![Image of Guna][S5]][S5]

### Syntax Color Scheme

Guna provides syntax color schemes for multiple programming languages, including [Python][L12], [Java][L13], [C++][L14], [Systemverilog][L15], [Html][L16], [Markdown][L17], [Yaml][L18], and more.

### API

Guna offers APIs to control its interface, such as functions to display alert situations. For example, typing <code>raise</code> in the Sublime console can demonstrate status bar label alerts. For more details, refer to [Guna's API documentation][L10].

<sup>(example - status bar label)</sup>  
![Image of Guna](https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/guna-alert-0.png)

### UI Scaling

Guna supports HiDPI with UI scaling. You can adjust the sizes of buttons, file icons, tabs, widgets, and switch panel icons in the [theme settings][L11].

```
{
	"scale": 1.5, // control sizes of buttons, file icons, tab ...
	"widget_scale": 1.33, // control sizes of clock, weather widget ...
	"switch_icon_scale": 1, // control the size of switch panel icon
}
```

### File Type Icons

While Guna doesn't include its own file type icons (except for Verilog/SystemVerilog), it is compatible with icon packages like [A File Icon][L7], which is recommended for use with Guna.

### Donate

[![Doate Image](https://raw.githubusercontent.com/poucotm/Links/master/image/PayPal/donate-paypal.png)][PM]  
If you find Guna helpful and would like to support its continued development, consider making a donation. Your contributions are appreciated and assist in the ongoing improvement of the plugin.

### Credits

- Icons designed by [Freepik](http://www.freepik.com/), [Dave Gandy](https://www.flaticon.com/authors/dave-gandy), [Madebyoliver](https://www.flaticon.com/authors/madebyoliver), [Gregor Cresnar](https://www.flaticon.com/authors/gregor-cresnar), [Smartline](https://www.flaticon.com/authors/smartline), [Vectors Market](https://www.flaticon.com/authors/vectors-market), [Monkik](https://www.flaticon.com/kr/authors/monkik), [Linector](https://www.flaticon.com/authors/Linector) from [www.flaticon.com](https://www.flaticon.com/)  is licensed by [CC 3.0 BY](http://creativecommons.org/licenses/by/3.0/)

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
[L11]:https://github.com/poucotm/Guna/blob/master/themes/preset/Guna-dark.sublime-settings "Guna Dark(Light) theme Settings"
[L12]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/python.png
[L13]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/java.png
[L14]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/cpp.png
[L15]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/systemverilog.png
[L16]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/html.png
[L17]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/markdown.png
[L18]:https://raw.githubusercontent.com/poucotm/Links/master/image/Guna/yaml.png
[PP]:https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=89YVNDSC7DZHQ "PayPal"
[PM]:https://www.paypal.me/poucotm/1.0 "PayPal"
[GUNA]:https://packagecontrol.io/packages/Guna "Guna"
