import unittest
from router import Router

class TestRouter(unittest.TestCase):
    def setUp(self):
        self.router_junos = Router(
            hostname    = 'vsrx1',
            os          = '12.1X47-D15.4',
            ipaddress   = '192.168.33.3',
            username    = 'user1',
            password    = 'password1')

    def test_get_hostname(self):
        expected    = self.router_junos.hostname
        actual      = self.router_junos.get_hostname()
        self.assertEqual(expected, actual)

if __name__ == "__main__":
    unittest.main()