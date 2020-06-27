""" myenergi """
import sys
from pprint import pprint
import os
import requests
from requests.auth import HTTPDigestAuth
import yaml

class myenergi:
  """ Implements the myenergi API """
  config = {}

  def __init__(self, config_path=f'{os.getcwd()}/config.yaml'):
    self.load_config(config_path)

  def load_config(self, config_path):
    """ Loads the configuration file """
    with open(config_path, 'r') as config_file:
      self.config = yaml.safe_load(config_file.read())

  def get_status(self):
    """ Returns the current API status """

    if 'hub_serial' not in self.config:
      print('Hub serial not found')
    if 'hub_password' not in self.config:
      print('Hub password not found')

    hub_serial = self.config['hub_serial']
    hub_password = self.config['hub_password']

    base_url = f'https://s{hub_serial[-1]}.myenergi.net'
    status_url = f'{base_url}/cgi-jstatus-Z'

    headers = {'User-Agent': 'Wget/1.14 (linux-gnu)'}
    auth = HTTPDigestAuth(hub_serial, hub_password)

    try:
      response = requests.get(status_url, headers=headers, auth=auth, timeout=10)
      print(response.status_code)
      pprint(response.json)
    except:
      print("Unexpected error:", sys.exc_info()[0])
      raise
