import unittest

import requests_mock

from libcloud_dnsimple_v2_driver.connection import LibCloudRequest


@requests_mock.Mocker()
class LibCloudRequestTests(unittest.TestCase):
    connection = None
    _test_url = "https://ifconfig.co/json"
    _response_json = {"ip": "46.101.192.233", "ip_decimal": 778420457, "country": "Germany", "country_eu": True,
                     "country_iso": "DE", "city": "Frankfurt am Main", "latitude": 50.1153, "longitude": 8.6823}
    _response_text = '{"ip":"46.101.192.233","ip_decimal":778420457,"country":"Germany",' +\
                     '"country_eu":true,"country_iso":"DE","city":"Frankfurt am Main",' +\
                     '"latitude":50.1153,"longitude":8.6823}'

    def setUp(self):
        self.connection = LibCloudRequest("user", "key")
        self.connection.host = "https://ifconfig.co"

    def set_mock_requests(self, m):
        m.get(self._test_url,
              #json=self._response_json,
              text=self._response_text,
              status_code=200,
              headers={
                  "cf-ray": "4528d1ce3bff9ac4-FRA",
                  "content-encoding": "br",
                  "content-type": "application/json",
                  "date": "Thu, 30 Aug 2018 17:01:28 GMT",
                  "expect-ct": "max-age=604800, report-uri=\"https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct\"",
                  "server": "cloudflare",
                  "status": "200",
                  "via": "1.1 vegur",
              })

    def test_request(self, m):
        self.set_mock_requests(m)
        response = self.connection.request("/json")

        self.assertEqual(response, self.connection)
        self.assertEqual(response.object["ip"], "46.101.192.233")

    def test_getresponse(self, m):
        self.set_mock_requests(m)
        self.connection.request("/json")
        response = self.connection.getresponse()

        self.assertEqual(response, self.connection)

    def test_getheaders(self, m):
        self.set_mock_requests(m)
        self.connection.request("/json")
        headers = self.connection.getheaders()

        self.assertNotIn("content-encoding", headers.keys())

    def test_status(self, m):
        self.set_mock_requests(m)
        self.connection.request("/json")

        self.assertEqual(self.connection.status, 200)

    def test_reason(self, m):
        self.set_mock_requests(m)
        self.connection.request("/json")

        self.assertEqual(self.connection.reason, self._response_text)

    def test_connect(self, m):
        self.set_mock_requests(m)
        self.assertEqual(self.connection.connect(), None)

    def test_read(self, m):
        self.set_mock_requests(m)
        self.connection.request("/json")
        data = self.connection.read()

        self.assertEqual(data, self._response_text.encode("utf-8"))

    def test_close(self, m):
        self.set_mock_requests(m)
        self.connection.request("/json")
        self.connection.close()