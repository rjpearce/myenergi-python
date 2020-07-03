""" myenergi """
import sys
from pprint import pprint
import os
import requests
from requests.auth import HTTPDigestAuth
import yaml
import json
from pathlib import Path


class MyEnergiDevice:
  name = ''
  attributes = {}
  translated_attributes = {}
  device = ''

  def __init__(self, attributes):
    self.device = self.__class__.__name__
    self.attributes = attributes
    self.name = f'{self.device}[{attributes["sno"]}]'
    self.id = f'{self.device[:1]}{attributes["sno"]}'
    self.translated_attributes = self.translate_attributes()

  def __repr__(self):
    return self.name

  def translate_value(self, attribute, value):
    with open(f'translations/{self.device}.yaml', 'r') as translation_file:
      translations = yaml.safe_load(translation_file.read())
      if 'values' in translations:
        if attribute in translations['values']:
          return translations['values'][attribute].get(value, value)
    return value

  def translate_attribute(self, attribute):
    with open(f'translations/{self.device}.yaml', 'r') as translation_file:
      translations = yaml.safe_load(translation_file.read())
      if 'attributes' in translations:
        return translations['attributes'].get(attribute, attribute)
    return attribute

  def translate_attributes(self):
    translated = {}
    for attr, value in self.attributes.items():
      tattr = self.translate_attribute(attr)
      tvalue = self.translate_value(attr, value)
      translated[tattr] = tvalue
    return translated

class Harvi(MyEnergiDevice):
  pass

class Eddi(MyEnergiDevice):
  pass

class Zappi(MyEnergiDevice):
  pass

class MyEnergi:
  """ Implements the myenergi API """
  config = {}
  devices = []
  connect_timeout = 10
  read_timeout = 30
  cache_folder = ''
  base_url = ''
  supported_devices = { 
    'Zappi': Zappi,
    'Harvi': Harvi,
    'Eddi': Eddi
   }

  def __init__(self, config_path=f'{str(Path.home())}/.myenergi.yaml', cache_folder=f'{os.getcwd()}/cache'):
    self.config = self.read_config(config_path)
    self.validate_config()
    self.cache_folder = cache_folder
    self.base_url = f'https://s{self.config["hub_serial"][-1]}.myenergi.net'
  
  def read_config(self, config_path):
    """ Read the configuration file """
    with open(config_path, 'r') as config_file:
      return yaml.safe_load(config_file.read())

  def validate_config(self):
    """ Validate the config """
    if 'hub_serial' not in self.config:
      raise Exception('hub_serial missing from config')
    if 'hub_password' not in self.config:
      raise Exception('hub_password missing from config')
    if 'use_cache' not in self.config:
      print('here')
      self.config['use_cache'] = False
  
  def request_status(self, endpoint='*'):
    status_url = f'{self.base_url}/cgi-jstatus-{endpoint}'

    headers = {'User-Agent': 'Wget/1.14 (linux-gnu)'}
    auth = HTTPDigestAuth(self.config['hub_serial'], self.config['hub_password'])
    response = requests.get(status_url, headers=headers, auth=auth, timeout=(self.connect_timeout, self.read_timeout))
    if response.status_code == 200:
      status_file = open(f'{self.cache_folder}/status.json', 'w')
      status_file.write(json.dumps(response.json()))
      status_file.close()
      return response.json()

  def get_all_devices(self):
    """ Returns the current API status """
    if self.config['use_cache']:
      with open(f'{self.cache_folder}/status.json') as data_file:    
        return json.load(data_file)
    return self.request_status('*')

  def populate_devices(self):
    data = self.get_all_devices()
    devices = []
    for device_list in data:
      for device, attributes_list in device_list.items():
        # Ignore asn
        if isinstance(attributes_list, (list)):
          # Ignore devices without any attributes
          if len(attributes_list) > 0:
            if device.capitalize() in self.supported_devices.keys():
              new_device = self.supported_devices[device.capitalize()](attributes_list[0])
              devices.append(new_device)
            else:
              raise Exception(f'Unsupported device {device}')
    self.devices = devices

  def list_devices(self):
    return list(map(str, self.devices))

def main(): 
  mye = MyEnergi()
  mye.populate_devices()
  for device in mye.devices:
    pprint(device.name)
    pprint(device.translated_attributes)

if __name__ == "__main__":
  main()
