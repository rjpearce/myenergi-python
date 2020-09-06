""" myenergi device """
import sys
from pprint import pprint
import os
import requests
from requests.auth import HTTPDigestAuth
import yaml
import json
from pathlib import Path
import math

class Translator:
  translations = {}
  WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

  def __init__(self, device):
    with open(f'myenergi/translations/{device}.yaml', 'r') as translation_file:
      self.translations = yaml.safe_load(translation_file.read())

  def days_from_myenergi(self, days):
    pprint(days)
    weekdays = ['unknown_prefix'] + self.WEEKDAYS
    translated_days = []
    for day in range(len(days)):
      if day == 0:
        continue
      else:
        if days[day] == '1': 
          translated_days.append(weekdays[day])
    if (len(translated_days) == 0):
      return 'None'
    return ','.join(translated_days)

  def days_to_myenergi(self, days):
    mydays = []
    for day in self.WEEKDAYS:
      mydays.append("1" if day in days else "0")
    return mydays.join('')

  def value(self, attribute, value):
    if attribute == 'bdd':
      return self.days_from_myenergi(value)
    if 'values' in self.translations:
      if attribute in self.translations['values']:
        return self.translations['values'][attribute].get(value, value)
    return value

  def attribute(self, attribute):
    if 'attributes' in self.translations:
      return self.translations['attributes'].get(attribute, attribute)
    return attribute
 
  def all_attributes(self, attributes):
    translated = {}
    for attr, value in attributes.items():
      tattr = self.attribute(attr)
      tvalue = self.value(attr, value)
      translated[tattr] = tvalue
    return translated

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