# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
import json
import os
import unittest
import requests_mock
from libcloud.dns.types import RecordType
from libcloud_dnsimple_v2_driver.dnsimple import DNSimpleV2DNSDriver

DNS_PARAMS_DNSIMPLE_V2 = ('user', 'key')


class DNSimpleV2DNSTests(unittest.TestCase):
    secure = True
    host = DNSimpleV2DNSDriver.host
    _test_domain = "example-alpha.com"

    def setUp(self):
        self.driver = DNSimpleV2DNSDriver(*DNS_PARAMS_DNSIMPLE_V2)

    def assertHasKeys(self, dictionary, keys):
        for key in keys:
            self.assertTrue(key in dictionary, 'key "%s" not in dictionary' %
                            (key))

    def _get_url(self, action):
        return "{}://{}{}".format(
            "https" if self.secure else "http",
            self.host,
            action,
        )

    def _get_fixture(self, ident):
        with open(os.path.join("fixtures", ident + ".json")) as f:
            return json.loads(f.read())

    def set_mock_requests(self, m):
        m.get(self._get_url(
            "/v2/{}/domains?per_page=100&page=1".format(DNS_PARAMS_DNSIMPLE_V2[0])),
            json=self._get_fixture("list_domains")
        )
        m.get(self._get_url(
            "/v2/{}/zones/{}/records?per_page=100&page=1".format(
                DNS_PARAMS_DNSIMPLE_V2[0],
                self._test_domain,
            )),
            json=self._get_fixture("list_records")
        )
        m.get(self._get_url(
            "/v2/{}/domains?per_page=100&page=1".format(DNS_PARAMS_DNSIMPLE_V2[0])),
            json=self._get_fixture("list_domains")
        )
        m.post(self._get_url(
            "/v2/{}/zones/{}/records".format(
                DNS_PARAMS_DNSIMPLE_V2[0],
                self._test_domain,
            )),
            json=self._get_fixture("create_record")
        )
        m.post(self._get_url(
            "/v2/{}/domains".format(
                DNS_PARAMS_DNSIMPLE_V2[0],
            )),
            json=self._get_fixture("create_domain")
        )
        m.get(self._get_url(
            "/v2/{}/domains/{}".format(
                DNS_PARAMS_DNSIMPLE_V2[0],
                self._test_domain,
            )),
            json=self._get_fixture("get_zone")
        )
        m.get(self._get_url(
            "/v2/{}/zones/{}/records/1".format(
                DNS_PARAMS_DNSIMPLE_V2[0],
                self._test_domain,
            )),
            json=self._get_fixture("get_record")
        )
        m.put(self._get_url("/v2/{}/zones/{}/records/1".format(
                DNS_PARAMS_DNSIMPLE_V2[0],
                self._test_domain,
            )),
            json=self._get_fixture("update_record")
        )
        m.delete(self._get_url("/v2/{}/domains/{}".format(
                DNS_PARAMS_DNSIMPLE_V2[0],
                self._test_domain,
            )
        ))
        m.delete(self._get_url("/v2/{}/zones/{}/records/69061".format(
            DNS_PARAMS_DNSIMPLE_V2[0],
            self._test_domain,
        )
        ))

    def test_list_record_types(self):
        record_types = self.driver.list_record_types()
        self.assertEqual(len(record_types), 15)
        self.assertTrue(RecordType.A in record_types)
        self.assertTrue(RecordType.AAAA in record_types)
        self.assertTrue(RecordType.ALIAS in record_types)
        self.assertTrue(RecordType.CNAME in record_types)
        self.assertTrue(RecordType.HINFO in record_types)
        self.assertTrue(RecordType.MX in record_types)
        self.assertTrue(RecordType.NAPTR in record_types)
        self.assertTrue(RecordType.NS in record_types)
        self.assertTrue('POOL' in record_types)
        self.assertTrue(RecordType.SPF in record_types)
        self.assertTrue(RecordType.SOA in record_types)
        self.assertTrue(RecordType.SRV in record_types)
        self.assertTrue(RecordType.SSHFP in record_types)
        self.assertTrue(RecordType.TXT in record_types)
        self.assertTrue(RecordType.URL in record_types)

    @requests_mock.Mocker()
    def test_list_zones_success(self, m):
        self.set_mock_requests(m)

        zones = self.driver.list_zones()
        self.assertEqual(len(zones), 2)

        zone1 = zones[0]
        self.assertEqual(zone1.id, 'example-alpha.com')
        self.assertEqual(zone1.type, 'master')
        self.assertEqual(zone1.domain, 'example-alpha.com')
        self.assertEqual(zone1.ttl, 3600)
        self.assertHasKeys(zone1.extra, ["account_id", "registrant_id", "unicode_name", "state", "auto_renew",
                                         "private_whois", "expires_on", "created_at", "updated_at"])

        zone2 = zones[1]
        self.assertEqual(zone2.id, 'example-beta.com')
        self.assertEqual(zone2.type, 'master')
        self.assertEqual(zone2.domain, 'example-beta.com')
        self.assertEqual(zone2.ttl, 3600)
        self.assertHasKeys(zone2.extra, ["account_id", "registrant_id", "unicode_name", "state", "auto_renew",
                                         "private_whois", "expires_on", "created_at", "updated_at"])

    @requests_mock.Mocker()
    def test_list_records_success(self, m):
        self.set_mock_requests(m)

        zone = self.driver.list_zones()[0]
        records = self.driver.list_records(zone=zone)
        self.assertEqual(len(records), 5)

        record1 = records[0]
        self.assertEqual(record1.id, '1')
        self.assertEqual(record1.name, '')
        self.assertEqual(record1.type, RecordType.SOA)
        self.assertEqual(record1.data, 'ns1.dnsimple.com admin.dnsimple.com 1458642070 86400 7200 604800 300')
        self.assertHasKeys(record1.extra, ["zone_id", "parent_id", "ttl", "priority", "regions", "system_record",
                                           "created_at", "updated_at"])

        record2 = records[1]
        self.assertEqual(record2.id, '69061')
        self.assertEqual(record2.name, '')
        self.assertEqual(record2.type, RecordType.NS)
        self.assertEqual(record2.data, 'ns1.dnsimple.com')
        self.assertHasKeys(record2.extra, ["zone_id", "parent_id", "ttl", "priority", "regions", "system_record",
                                           "created_at", "updated_at"])

        record3 = records[2]
        self.assertEqual(record3.id, '2')
        self.assertEqual(record3.name, '')
        self.assertEqual(record3.type, RecordType.NS)
        self.assertEqual(record3.data, 'ns2.dnsimple.com')
        self.assertHasKeys(record3.extra, ["zone_id", "parent_id", "ttl", "priority", "regions", "system_record",
                                           "created_at", "updated_at"])

        record4 = records[3]
        self.assertEqual(record4.id, '3')
        self.assertEqual(record4.name, '')
        self.assertEqual(record4.type, RecordType.NS)
        self.assertEqual(record4.data, 'ns3.dnsimple.com')
        self.assertHasKeys(record4.extra, ["zone_id", "parent_id", "ttl", "priority", "regions", "system_record",
                                           "created_at", "updated_at"])

        record5 = records[4]
        self.assertEqual(record5.id, '4')
        self.assertEqual(record5.name, '')
        self.assertEqual(record5.type, RecordType.NS)
        self.assertEqual(record5.data, 'ns4.dnsimple.com')
        self.assertHasKeys(record5.extra, ["zone_id", "parent_id", "ttl", "priority", "regions", "system_record",
                                           "created_at", "updated_at"])

    @requests_mock.Mocker()
    def test_create_record_success(self, m):
        self.set_mock_requests(m)

        zone = self.driver.list_zones()[0]
        record = self.driver.create_record(name='foo', zone=zone,
                                           type=RecordType.MX,
                                           data='mail.example-alpha.com', extra={"priority": 10})

        self.assertEqual(record.id, '1')
        self.assertEqual(record.name, 'foo')
        self.assertEqual(record.type, RecordType.MX)
        self.assertEqual(record.data, 'mail.example-alpha.com')
        self.assertHasKeys(record.extra, ["zone_id", "parent_id", "ttl", "priority", "regions", "system_record",
                                          "created_at", "updated_at"])

    @requests_mock.Mocker()
    def test_create_zone_success(self, m):
        self.set_mock_requests(m)

        zone = self.driver.create_zone(domain='example-alpha.com')
        self.assertEqual(zone.id, 'example-alpha.com')
        self.assertEqual(zone.domain, 'example-alpha.com')
        self.assertEqual(zone.ttl, 3600)
        self.assertEqual(zone.type, 'master')
        self.assertHasKeys(zone.extra, ["id", "account_id", "registrant_id", "unicode_name", "state", "auto_renew",
                                        "private_whois", "expires_on", "created_at", "updated_at", ])

    @requests_mock.Mocker()
    def test_get_zone_success(self, m):
        self.set_mock_requests(m)

        zone1 = self.driver.get_zone(zone_id='example-alpha.com')
        self.assertEqual(zone1.id, 'example-alpha.com')
        self.assertEqual(zone1.type, 'master')
        self.assertEqual(zone1.domain, 'example-alpha.com')
        self.assertHasKeys(zone1.extra, ["account_id", "registrant_id", "unicode_name", "state", "auto_renew",
                                         "private_whois", "expires_on", "created_at", "updated_at"])

    @requests_mock.Mocker()
    def test_get_record_success(self, m):
        self.set_mock_requests(m)

        record = self.driver.get_record(zone_id='example-alpha.com',
                                        record_id='1')
        self.assertEqual(record.id, '1')
        self.assertEqual(record.name, '')
        self.assertEqual(record.type, RecordType.MX)
        self.assertEqual(record.data, 'mxa.example-alpha.com')
        self.assertHasKeys(record.extra, ["zone_id", "parent_id", "ttl", "priority", "regions", "system_record",
                                           "created_at", "updated_at"])

    @requests_mock.Mocker()
    def test_update_record_success(self, m):
        self.set_mock_requests(m)

        record = self.driver.get_record(zone_id='example-alpha.com',
                                        record_id='1')
        record1 = self.driver.update_record(
            record=record,
            name='www',
            data='updated.com',
            extra={
                'ttl': 4500
            },
            type=None,
        )

        self.assertEqual(record.data, 'mxa.example-alpha.com')
        self.assertEqual(record.extra.get('ttl'), 3600)
        self.assertEqual(record1.data, 'updated.com')
        self.assertEqual(record1.extra.get('ttl'), 4500)

    @requests_mock.Mocker()
    def test_delete_zone_success(self, m):
        self.set_mock_requests(m)

        zone = self.driver.list_zones()[0]
        status = self.driver.delete_zone(zone=zone)
        self.assertTrue(status)

    @requests_mock.Mocker()
    def test_delete_record_success(self, m):
        self.set_mock_requests(m)

        zone = self.driver.list_zones()[0]
        records = self.driver.list_records(zone=zone)
        self.assertEqual(len(records), 5)
        record = records[1]
        status = self.driver.delete_record(record=record)
        self.assertTrue(status)

# if __name__ == '__main__':
#     sys.exit(unittest.main())
