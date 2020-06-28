""" Implemented testing for the myenergi module """
import unittest
import os
from myenergi import myenergi

class TestMyEnergiClass(unittest.TestCase):
  """Test MyEnergy Class"""

  def test_config_loads_correctly(self):
    """it should load config correctly"""
    mye = myenergi(f'{os.getcwd()}/tests/fixtures/config_example.yaml')
    expected_config = {'hub_serial': '12345678', 'hub_password': 'secret'}
    self.assertDictEqual(mye.config, expected_config)

  def test_status(self):
    """it should load config correctly"""
    config_file = f'{os.getcwd()}/tests/fixtures/config_example.yaml'
    cache_folder = f'{os.getcwd()}/tests/fixtures'
    mye = myenergi(config_file, cache_folder)
    self.assertListEqual(mye.list_devices(), ['zappi_12345678'])

if __name__ == '__main__':
  unittest.main()
