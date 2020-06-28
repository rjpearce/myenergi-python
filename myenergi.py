""" myenergi """
import sys
from pprint import pprint
import os
import requests
from requests.auth import HTTPDigestAuth
import yaml
import json
import simplejson

class myenergi:
  """ Implements the myenergi API """
  config = {}
  connect_timeout = 10
  read_timeout = 30

  def __init__(self, config_path=f'{os.getcwd()}/config.yaml'):
    self.load_config(config_path)
    self.validate_config()
  
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

  def get_zappi_status(self):
    """ Returns the current API status """

    hub_serial = self.config['hub_serial']
    hub_password = self.config['hub_password']

    base_url = f'https://s{hub_serial[-1]}.myenergi.net'
    status_url = f'{base_url}/cgi-jstatus-*'

    headers = {'User-Agent': 'Wget/1.14 (linux-gnu)'}
    auth = HTTPDigestAuth(hub_serial, hub_password)
    response = requests.get(status_url, headers=headers, auth=auth, timeout=(self.connect_timeout, self.read_timeout))
    print(response.status_code)
    status_file = open("status.json", "w")
    status_file.write(json.dumps(response.json()))
    status_file.close()

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
  
  def translate_response(self, response_json):
    translated = {}
    for device_list in response_json:
      for device, attributes_list in device_list.items():
        translated[device] = {}
        for attributes in attributes_list:
          if isinstance(attributes, (dict)):
            for attr, value in attributes.items():
              tvalue = self.translate_value(attr, value, device)
              translated[device][self.translate_attribute(attr, device)] = tvalue
          else:
              translated[device] = attributes_list
    return translated


def main(): 
  mye = myenergi()
  #mye.get_zappi_status()

  with open('tests/fixtures/status.json') as data_file:    
    data = json.load(data_file)
    pprint(mye.translate_response(data))

if __name__ == "__main__":
  main()
