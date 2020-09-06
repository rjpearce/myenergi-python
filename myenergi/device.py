""" myenergi device """
import sys
from pprint import pprint
import os
import requests
from requests.auth import HTTPDigestAuth
import json
from pathlib import Path
import math
from .translator import Translator

class Device:
  name = ''
  attributes = {}
  translated_attributes = {}
  device = ''
  myenergi = None

  def __init__(self, myenergi, attributes):
    self.device = self.__class__.__name__
    self.myenergi = myenergi
    self.attributes = attributes
    self.name = f'{self.device}[{attributes["sno"]}]'
    self.id = f'{self.device[:1]}{attributes["sno"]}'
    self.translate = Translator(self.device)
    self.translated_attributes = self.translate.all_attributes(self.attributes)  

  def __repr__(self):
    return self.name

class Harvi(Device):
  pass

class Eddi(Device):
  pass

class Zappi(Device):
  boost_times = []
  translated_boost_times = []

  def get_boost_times(self, translate=True):
    response_json = self.myenergi.api_request(f'{self.myenergi.base_url}/cgi-boost-time-{self.id}')
    if translate:
      self.translated_boost_times = []
      for boost_time in response_json['boost_times']:
        self.translated_boost_times.append(self.translate.all_attributes(boost_time))
      return self.translated_boost_times
    else:
      return response_json['boost_times']
  
  def set_boot_times_for_slot(self, slot, start_time, duration_mins, days):
    duration_hours = math.floor(duration_mins / 60)
    duration_mins = duration_mins - (duration_hours * 60)
    boost_url = (
      f'{self.myenergi.base_url}/cgi-boost-time-{self.id}'  
      f'-{slot}'
      f'-{start_time.replace(":","")}'
      f'-{duration_hours}{duration_mins}'
      f'-{days}'
    )
    response_json = self.myenergi.api_request(boost_url)