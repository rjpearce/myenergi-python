import yaml

class Translator:
  translations = {}
  WEEKDAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

  def __init__(self, device):
    with open(f'myenergi/translations/{device}.yaml', 'r') as translation_file:
      self.translations = yaml.safe_load(translation_file.read())

  def days_from_myenergi(self, days):
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
    mydays = ['0']
    for day in self.WEEKDAYS:
      mydays.append("1" if day in days else "0")
    return ''.join(mydays)

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