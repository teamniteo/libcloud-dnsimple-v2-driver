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
import sys
import unittest

from libcloud.utils.py3 import httplib

from libcloud.dns.types import RecordType

from libcloud.test import MockHttp
from libcloud.test.file_fixtures import FileFixtures

from dnsimple import DNSimpleV2DNSDriver, DNSimpleV2DNSConnection

DNS_PARAMS_DNSIMPLE_V2 = ('user', 'key')


class DNSimpleV2DNSConnectionTests(unittest.TestCase):

    def test_dnsimple_v2_connection(self):
        connection = DNSimpleV2DNSConnection("user", "key")
        headers = connection.add_default_headers({})

        self.assertDictEqual(
            headers,
            {
                "Authorization": "Bearer key",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )


class DNSimpleV2DNSTests(unittest.TestCase):

    def setUp(self):
        DNSimpleV2DNSDriver.connectionCls.conn_class = DNSimpleV2DNSMockHttp
        DNSimpleV2DNSMockHttp.type = None
        self.driver = DNSimpleV2DNSDriver(*DNS_PARAMS_DNSIMPLE_V2)

    def assertHasKeys(self, dictionary, keys):
        for key in keys:
            self.assertTrue(key in dictionary, 'key "%s" not in dictionary' %
                            (key))

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

    def test_list_zones_success(self):
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

    def test_list_records_success(self):
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

    def test_create_record_success(self):
        zone = self.driver.list_zones()[0]
        DNSimpleV2DNSMockHttp.type = 'CREATE'
        record = self.driver.create_record(name='foo', zone=zone,
                                           type=RecordType.MX,
                                           data='mail.example-alpha.com', extra={"priority": 10})

        self.assertEqual(record.id, '1')
        self.assertEqual(record.name, 'foo')
        self.assertEqual(record.type, RecordType.MX)
        self.assertEqual(record.data, 'mail.example-alpha.com')
        self.assertHasKeys(record.extra, ["zone_id", "parent_id", "ttl", "priority", "regions", "system_record",
                                          "created_at", "updated_at"])

    def test_create_zone_success(self):
        DNSimpleV2DNSMockHttp.type = 'CREATE'
        zone = self.driver.create_zone(domain='example-alpha.com')
        self.assertEqual(zone.id, 'example-alpha.com')
        self.assertEqual(zone.domain, 'example-alpha.com')
        self.assertEqual(zone.ttl, 3600)
        self.assertEqual(zone.type, 'master')
        self.assertHasKeys(zone.extra, ["id", "account_id", "registrant_id", "unicode_name", "state", "auto_renew",
                                        "private_whois", "expires_on", "created_at", "updated_at", ])

    def test_get_zone_success(self):
        zone1 = self.driver.get_zone(zone_id='example-alpha.com')
        self.assertEqual(zone1.id, 'example-alpha.com')
        self.assertEqual(zone1.type, 'master')
        self.assertEqual(zone1.domain, 'example-alpha.com')
        self.assertHasKeys(zone1.extra, ["account_id", "registrant_id", "unicode_name", "state", "auto_renew",
                                         "private_whois", "expires_on", "created_at", "updated_at"])

    def test_get_record_success(self):
        record = self.driver.get_record(zone_id='example-alpha.com',
                                        record_id='1')
        self.assertEqual(record.id, '1')
        self.assertEqual(record.name, '')
        self.assertEqual(record.type, RecordType.MX)
        self.assertEqual(record.data, 'mxa.example-alpha.com')
        self.assertHasKeys(record.extra, ["zone_id", "parent_id", "ttl", "priority", "regions", "system_record",
                                           "created_at", "updated_at"])

    def test_update_record_success(self):
        record = self.driver.get_record(zone_id='example-alpha.com',
                                        record_id='1')
        DNSimpleV2DNSMockHttp.type = 'UPDATE'
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

    def test_delete_zone_success(self):
        zone = self.driver.list_zones()[0]
        DNSimpleV2DNSMockHttp.type = 'DELETE_204'
        status = self.driver.delete_zone(zone=zone)
        self.assertTrue(status)

    def test_delete_record_success(self):
        zone = self.driver.list_zones()[0]
        records = self.driver.list_records(zone=zone)
        self.assertEqual(len(records), 5)
        record = records[1]
        DNSimpleV2DNSMockHttp.type = 'DELETE_204'
        status = self.driver.delete_record(record=record)
        self.assertTrue(status)


class DNSimpleV2Fixtures(FileFixtures):

    def __init__(self, fixtures_type, sub_dir=''):
        super().__init__(fixtures_type, sub_dir)
        self.root = "fixtures"


class DNSimpleV2DNSMockHttp(MockHttp):
    fixtures = DNSimpleV2Fixtures("dns")

    def _v2_user_domains(self, method, url, body, headers):
        body = self.fixtures.load('list_domains.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v2_user_zones_example_alpha_com_records(self, method, url, body, headers):
        body = self.fixtures.load('list_records.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v2_user_domains_CREATE(self, method, url, body, headers):
        body = self.fixtures.load('create_domain.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v2_user_zones_example_alpha_com_records_CREATE(self, method, url, body, headers):
        body = self.fixtures.load('create_record.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v2_user_zones_example_alpha_com_records_1(self, method, url, body, headers):
        body = self.fixtures.load('get_record.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v2_user_zones_example_alpha_com_records_1_UPDATE(self, method, url, body, headers):
        body = self.fixtures.load('update_record.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v2_user_domains_example_alpha_com(self, method, url, body, headers):
        body = self.fixtures.load('get_zone.json')
        return (httplib.OK, body, {}, httplib.responses[httplib.OK])

    def _v2_user_domains_example_alpha_com_DELETE_204(self, method, url, body, headers):
        return (httplib.OK, '', {}, httplib.responses[httplib.NO_CONTENT])

    def _v2_user_zones_example_alpha_com_records_69061_DELETE_204(self, method, url, body, headers):
        return (httplib.OK, '', {}, httplib.responses[httplib.NO_CONTENT])



# if __name__ == '__main__':
#     sys.exit(unittest.main())
