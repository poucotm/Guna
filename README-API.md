
#### Guna's API

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

GunaApi.info(flag=0, onoff=False):
    """
    Makes the clock, status bar red for alarming

    flag = GunaApi.INFO_CLOCK | GunaApi.ALRT_STATUS_LABEL
    """

GunaApi.info_message(flag=0, message='', timeout=4, action=0):
    """
    Makes red with a status message in a timeout(seconds).
    Within a timeout, a new message request will be ignored (will be replaced as a queue).

    action = GunaApi.FLICKER
    """
```
