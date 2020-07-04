# myenergi-python

[![codecov](https://codecov.io/gh/rjpearce/myenergi-python/branch/master/graph/badge.svg)](https://codecov.io/gh/rjpearce/myenergi-python)

This module provides an open-source implementation of the myenergy's closed API in Python.
It is currently in the early stages of development, contributions are always welcome but it will be a fast moving target

If you want an API that is already working checkout this one:
* https://github.com/ashleypittman/mec

## Legal Disclaimer

This module is un-official and is not endorsed or associated with myenergi

The software is provided “as is”, without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement. in no event shall the authors or copyright holders be liable for any claim, damages or other liability, whether in an action of contract, tort or otherwise, arising from, out of or in connection with the softwares or the use or mis-used or other dealings in the software.

## Recognition

This project would not have been possible without the hard work of others:
* https://github.com/twonk/MyEnergi-App-Api
* https://github.com/leo389/myenergi_scripts

## Setup

Create a config file in ~/.myenergy.yaml

```yaml
---
hub_serial: '12345678'
hub_password: 'secret'
use_cache: False
...
```

### Settings

* use_cache - True - Use the cache/status.json file from the last run instead of querying myenergi API.

## Usage

```python

from myenergi import MyEnergi

  mye = MyEnergi()
  
  # Query the myenergi API to obtain devices
  mye.populate_devices()
  
  # Output the devices with attributes translated into human friendly wording
  for device in mye.devices:
    pprint(device.name)
    pprint(device.translated_attributes)
```

## Contribute

Please do feel free to fork this module it enhance it for the benefit of everyone.
