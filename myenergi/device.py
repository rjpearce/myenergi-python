""" myenergi device """
import sys
from pprint import pprint
import os
import requests
from requests.auth import HTTPDigestAuth
import yaml
import json
from pathlib import Path

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
    self.translated_attributes = self.translate(self.attributes)

  def __repr__(self):
    return self.name

  def translate_days_value(self, days):
    weekdays = ['?', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    translated_days = []
    for day in range(len(days)):
      if days[day] == '1': 
        translated_days.append(weekdays[day])
    if (len(translated_days) == 0):
      return 'None'
    return ','.join(translated_days)

  def translate_value(self, attribute, value):
    with open(f'myenergi/translations/{self.device}.yaml', 'r') as translation_file:
      translations = yaml.safe_load(translation_file.read())
      if attribute == 'bdd':
        return self.translate_days_value(value)
      if 'values' in translations:
        if attribute in translations['values']:
          return translations['values'][attribute].get(value, value)
    return value

  def translate_attribute(self, attribute):
    with open(f'myenergi/translations/{self.device}.yaml', 'r') as translation_file:
      translations = yaml.safe_load(translation_file.read())
      if 'attributes' in translations:
        return translations['attributes'].get(attribute, attribute)
    return attribute
 
  def translate(self, attributes):
    translated = {}
    for attr, value in attributes.items():
      tattr = self.translate_attribute(attr)
      tvalue = self.translate_value(attr, value)
      translated[tattr] = tvalue
    return translated

class Harvi(Device):
  pass

class Eddi(Device):
  pass

class Zappi(Device):
  boost_times = []
  translated_boost_times = []

  def get_boost_times(self, translate=True):
    self.translated_boost_times = []
    response_json = self.myenergi.api_request(f'{self.myenergi.base_url}/cgi-boost-time-{self.id}')
    self.boost_times = response_json['boost_times']
    for boost_time in response_json['boost_times']:
      self.translated_boost_times.append(self.translate(boost_time))
    if translate: 
      return self.translated_boost_times
    return self.boost_times
