import sys
from pprint import pprint
sys.path.append('.')
import myenergi 

mec = myenergi.Client()
mec.populate_devices()
for device in mec.devices:
  if isinstance(device, (myenergi.Zappi)):
    pprint(device.name)
    pprint(device.get_boost_times())
    pprint(device.translated_attributes)