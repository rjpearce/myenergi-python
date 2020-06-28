""" myenergi """
import sys
from pprint import pprint
import os
import requests
from requests.auth import HTTPDigestAuth
import yaml
import json

class zappi:
  name = ''
  attributes = {}

  def __init__(self, attributes):
    self.attributes = attributes
    self.name = f'zappi_{attributes["sno"]}'

  def __repr__(self):
    return self.name

class myenergi:
  """ Implements the myenergi API """
  config = {}
  devices = []
  connect_timeout = 10
  read_timeout = 30
  use_cache = True

  def __init__(self, config_path=f'{os.getcwd()}/config.yaml'):
    self.load_config(config_path)
    self.validate_config()
    self.devices = self.populate_devices()
  
  def load_config(self, config_path):
    """ Loads the configuration file """
    with open(config_path, 'r') as config_file:
      self.config = yaml.safe_load(config_file.read())

  def validate_config(self):
    """ Validate the config """
    if 'hub_serial' not in self.config:
      raise Exception('hub_serial missing from config')
    if 'hub_password' not in self.config:
      print('Hub password not found')
      raise Exception('hub_password missing from config')
  
    

  def request_status(self, endpoint='*'):
    hub_serial = self.config['hub_serial']
    hub_password = self.config['hub_password']

    base_url = f'https://s{hub_serial[-1]}.myenergi.net'
    status_url = f'{base_url}/cgi-jstatus-{endpoint}'

    headers = {'User-Agent': 'Wget/1.14 (linux-gnu)'}
    auth = HTTPDigestAuth(hub_serial, hub_password)
    response = requests.get(status_url, headers=headers, auth=auth, timeout=(self.connect_timeout, self.read_timeout))
    if response.status_code == 200:
      status_file = open("status.json", "w")
      status_file.write(json.dumps(response.json()))
      status_file.close()
      return response.json()

  def get_all_devices(self):
    """ Returns the current API status """
    if self.use_cache:
      with open('tests/fixtures/status.json') as data_file:    
        return json.load(data_file)
    return self.request_status('*')

  def translate_value(self, attribute, value, device):
    if device in ('zappi', 'eddi'):
      with open(f'translations/{device}.yaml', 'r') as translation_file:
        translations = yaml.safe_load(translation_file.read())
        if attribute in translations['values']:
          return translations['values'][attribute].get(value, value)
    return value

  def translate_attribute(self, attribute, device):
    if device in ('zappi', 'harvi', 'eddi'):
      with open(f'translations/{device}.yaml', 'r') as translation_file:
        translations = yaml.safe_load(translation_file.read())
        return translations['attributes'].get(attribute, attribute)
    return attribute

  def populate_devices(self):
    data = self.get_all_devices()
    devices = []
    for device_list in data:
      for device, attributes_list in device_list.items():
        # Ignore asn
        if isinstance(attributes_list, (list)):
          # Ignore devices without any attributes
          if len(attributes_list) > 0:
            if device in ('zappi'):
              devices.append(zappi(attributes_list[0]))
    return devices

  def translate_response(self, response_json):
    translated = {}
    for device_list in response_json:
      for device, attributes_list in device_list.items():
        # Ignore asn
        if isinstance(attributes_list, (list)):
          # Ignore devices without any attributes
          if len(attributes_list) > 0:
            translated[device] = {}
            if isinstance(attributes_list[0], (dict)):
              for attr, value in attributes_list[0].items():
                tvalue = self.translate_value(attr, value, device)
                translated[device][self.translate_attribute(attr, device)] = tvalue
            else:
              translated[device] = attributes_list
    return translated

def main(): 
  mye = myenergi()
  pprint(mye.devices)

if __name__ == "__main__":
  main()
