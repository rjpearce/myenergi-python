""" Implemented testing for the myenergi module """
import unittest
import os
import unittest
import urllib.request
import httptest
import myenergi 

class TestClient(unittest.TestCase):
  """Test MyEnergi Client Class"""

  def test_config_parses(self):
    """it should parse config correctly"""
    mec = myenergi.Client(f'{os.getcwd()}/tests/fixtures/config_cache.yaml')
    expected_config = {
      'hub_serial': '12345678',
      'hub_password': 'secret',
      'use_cache': True
    }
    self.assertDictEqual(mec.config, expected_config)

  def test_fails_for_bad_config(self):
    """it should fail for bad config"""
    config_file = f'{os.getcwd()}/tests/fixtures/config_bad.yaml'
    with self.assertRaisesRegex(Exception, 'missing from config'):
      myenergi.Client(config_file)

  def test_parses_cached_devices(self):
    """it should parse cached devices """
    config_file = f'{os.getcwd()}/tests/fixtures/config_cache.yaml'
    cache_folder = f'{os.getcwd()}/tests/fixtures'
    mec = myenergi.Client(config_file, cache_folder)
    mec.populate_devices()
    self.assertListEqual(mec.list_devices(), ['Zappi[12345678]', 'Harvi[12345678]'])

class TestTranslator(unittest.TestCase):
  """Test MyEnergi Translator Class"""
  
  def test_days_value_to_myenergi(self):
    translator = myenergi.Translator('Zappi')
    expected = 'Mon,Tue,Wed,Thu,Fri,Sat,Sun'
    actual = translator.days_from_myenergi('11111111')
    self.assertEqual(expected, actual)

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
    mec = myenergi.Client(config_file)
    mec.base_url = ts.url().replace('1.0.0.127.in-addr.arpa','127.0.0.1')
    mec.populate_devices()
    self.assertListEqual(mec.list_devices(), ['Zappi[12345678]', 'Harvi[12345678]'])

if __name__ == '__main__':
  unittest.main()
