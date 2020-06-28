""" Implemented testing for the myenergi module """
import unittest
import os
import unittest
import urllib.request
import httptest
from myenergi import myenergi

class TestMyEnergiClass(unittest.TestCase):
  """Test MyEnergy Class"""

  def test_config_loads_correctly(self):
    """it should load config correctly"""
    mye = myenergi(f'{os.getcwd()}/tests/fixtures/config_cache.yaml')
    expected_config = {
      'hub_serial': '12345678',
      'hub_password': 'secret',
      'use_cache': True,
    }
    self.assertDictEqual(mye.config, expected_config)

  def test_status(self):
    """it should load config correctly"""
    config_file = f'{os.getcwd()}/tests/fixtures/config_cache.yaml'
    cache_folder = f'{os.getcwd()}/tests/fixtures'
    mye = myenergi(config_file, cache_folder)
    mye.populate_devices()
    self.assertListEqual(mye.list_devices(), ['zappi_12345678'])


class TestHTTPServer(httptest.Handler):

  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "application/json")
    self.end_headers()
    with open( f'{os.getcwd()}/tests/fixtures/status.json', 'r') as response_file:
      self.wfile.write(bytes(response_file.read(),'utf8'))

class TestHTTPTestMethods(unittest.TestCase):

  @httptest.Server(TestHTTPServer)
  def test_call_response(self, ts=httptest.NoServer()):
    config_file = f'{os.getcwd()}/tests/fixtures/config_nocache.yaml'
    cache_folder = f'{os.getcwd()}/tests/fixtures'
    mye = myenergi(config_file)
    mye.base_url = ts.url()
    mye.populate_devices()
    self.assertListEqual(mye.list_devices(), ['zappi_12345678'])

  def test_status(self):
    """it should fail for bad config"""
    config_file = f'{os.getcwd()}/tests/fixtures/config_bad.yaml'
    with self.assertRaisesRegex(Exception, 'missing from config'):
      myenergi(config_file)

if __name__ == '__main__':
  unittest.main()
