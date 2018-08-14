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
# limitations under the License.
"""
DNSimple v2 DNS Driver
"""
from libcloud.common.base import ConnectionUserAndKey

__all__ = [
    'DNSimpleV2DNSDriver'
]

try:
    import simplejson as json
except ImportError:
    import json

from libcloud.common.dnsimple import DNSimpleDNSResponse
from libcloud.dns.types import RecordType
from libcloud.dns.base import DNSDriver, Zone, Record


DEFAULT_ZONE_TTL = 3600


class DNSimpleV2DNSConnection(ConnectionUserAndKey):
    """
    user_id: put account ID, you can find it here: https://dnsimple.com/a/<ACCOUNT_ID>/account
    key: API token taken from the admin interface
    """

    host = 'api.dnsimple.com'
    responseCls = DNSimpleDNSResponse

    def add_default_headers(self, headers):
        """
        Add headers that are necessary for every request

        This method adds ``token`` to the request.
        """
        headers['Authorization'] = 'Bearer {}'.format(self.key)
        headers['Accept'] = 'application/json'
        headers['Content-Type'] = 'application/json'
        return headers


class DNSimpleV2DNSDriver(DNSDriver):
    type = "DNSimpleV2"
    name = 'DNSimpleV2'
    website = 'https://dnsimple.com/'
    connectionCls = DNSimpleV2DNSConnection

    RECORD_TYPE_MAP = {
        RecordType.A: 'A',
        RecordType.AAAA: 'AAAA',
        RecordType.ALIAS: 'ALIAS',
        RecordType.CNAME: 'CNAME',
        RecordType.HINFO: 'HINFO',
        RecordType.MX: 'MX',
        RecordType.NAPTR: 'NAPTR',
        RecordType.NS: 'NS',
        'POOL': 'POOL',
        RecordType.SOA: 'SOA',
        RecordType.SPF: 'SPF',
        RecordType.SRV: 'SRV',
        RecordType.SSHFP: 'SSHFP',
        RecordType.TXT: 'TXT',
        RecordType.URL: 'URL'
    }

    def iterate_zones(self):
        """
        Return a list of zones.

        :return: ``list`` of :class:`Zone`
        """
        page_number = 1

        while True:
            response = self.connection.request('/v2/{}/domains?per_page=100&page={}'.format(
                    self.connection.user_id,
                    page_number,
                )
            )
            for zone in self._to_zones(response.object.get("data")):
                yield zone

            pagination = response.object.get("pagination")
            page_number = pagination["current_page"] + 1
            if pagination["current_page"] >= pagination["total_pages"]:
                break

    def iterate_records(self, zone):
        """
        Return a list of records for the provided zone.

        :param zone: Zone to list records for.
        :type zone: :class:`Zone`

        :return: ``list`` of :class:`Record`
        """
        page_number = 1

        while True:
            response = self.connection.request(
                '/v2/{}/zones/{}/records?per_page=100&page={}'.format(
                    self.connection.user_id,
                    zone.id,
                    page_number,
                )
            )
            for record in self._to_records(response.object.get("data"), zone):
                yield record

            pagination = response.object.get("pagination")
            page_number = pagination["current_page"] + 1
            if pagination["current_page"] >= pagination["total_pages"]:
                break

    def get_zone(self, zone_id):
        """
        Return a Zone instance.

        :param zone_id: ID of the required zone
        :type  zone_id: ``str``

        :rtype: :class:`Zone`
        """
        response = self.connection.request('/v2/{}/domains/{}'.format(self.connection.user_id, zone_id))
        zone = self._to_zone(response.object.get("data"))
        return zone

    def get_record(self, zone_id, record_id):
        """
        Return a Record instance.

        :param zone_id: ID of the required zone
        :type  zone_id: ``str``

        :param record_id: ID of the required record
        :type  record_id: ``str``

        :rtype: :class:`Record`
        """
        response = self.connection.request('/v2/{}/zones/{}/records/{}'.format(
            self.connection.user_id,
            zone_id,
            record_id,
        ))
        record = self._to_record(response.object.get("data"), zone_id=zone_id)
        return record

    def create_zone(self, domain, type='master', ttl=None, extra=None):
        """
        Create a new zone. This one actually creates a new domain but
        the zone is created alongside the domain. The zone can't be
        updated, because there is no way how to change type or TTL.

        :param domain: Domain name (e.g. example.com)
        :type domain: ``str``

        :param type: not used
        :type  type: None

        :param ttl: not used
        :type  ttl: None

        :param extra: not used
        :type extra: None

        :rtype: :class:`Zone`

        For more info, please see:
        https://developer.dnsimple.com/v2/domains/
        """
        r_json = {'name': domain}

        r_data = json.dumps(r_json)

        response = self.connection.request(
            '/v2/{}/domains'.format(self.connection.user_id), method='POST', data=r_data)
        zone = self._to_zone(response.object.get("data"))
        return zone

    def create_record(self, name, zone, type, data, extra=None):
        """
        Create a new record.

        :param name: Record name without the domain name (e.g. www).
                     Note: If you want to create a record for a base domain
                     name, you should specify empty string ('') for this
                     argument.
        :type  name: ``str``

        :param zone: Zone where the requested record is created.
        :type  zone: :class:`Zone`

        :param type: DNS record type (A, AAAA, ...).
        :type  type: :class:`RecordType`

        :param data: Data for the record (depends on the record type).
        :type  data: ``str``

        :param extra: Extra attributes (driver specific). (optional)
        :type extra: ``dict``

        :rtype: :class:`Record`
        """

        r_json = {
            'name': name,
            'type': type,
            'content': data
        }

        if extra is not None:
            r_json.update(extra)

        r_data = json.dumps(r_json)

        response = self.connection.request(
            '/v2/{}/zones/{}/records'.format(
                self.connection.user_id,
                zone.id
            ),
            method='POST',
            data=r_data,
        )
        record = self._to_record(response.object.get("data"), zone=zone)
        return record

    def update_record(self, record, name, type, data, extra=None):
        """
        Update an existing record.

        :param record: Record to update.
        :type  record: :class:`Record`

        :param name: Record name without the domain name (e.g. www).
                     Note: If you want to create a record for a base domain
                     name, you should specify empty string ('') for this
                     argument.
        :type  name: ``str``

        :param type: can't be changed in DNSimple's API
        :type  type: None

        :param data: Data for the record (depends on the record type).
        :type  data: ``str``

        :param extra: (optional) Extra attributes (driver specific).
        :type  extra: ``dict``

        :rtype: :class:`Record`
        """
        zone = record.zone

        r_json = {
            'name': name,
            'content': data
        }

        if extra is not None:
            r_json.update(extra)

        r_data = json.dumps({'record': r_json})

        response = self.connection.request(
            '/v2/{}/zones/{}/records/{}'.format(
                self.connection.user_id,
                zone.id,
                record.id
            ),
            method='PUT',
            data=r_data,
        )
        record = self._to_record(response.object.get("data"), zone=zone)
        return record

    def delete_zone(self, zone):
        """
        Delete a zone.

        Note: This will delete all the records belonging to this zone.

        :param zone: Zone to delete.
        :type  zone: :class:`Zone`

        :rtype: ``bool``
        """
        self.connection.request('/v2/{}/domains/{}'.format(self.connection.user_id, zone.id), method='DELETE')
        return True

    def delete_record(self, record):
        """
        Delete a record.

        :param record: Record to delete.
        :type  record: :class:`Record`

        :rtype: ``bool``
        """
        zone_id = record.zone.id

        self.connection.request('/v2/{}/zones/{}/records/{}'.format(
            self.connection.user_id,
            zone_id,
            record.id,
        ), method='DELETE')

        return True

    def _to_zones(self, data):
        # TODO: upgrade this to v2
        zones = []
        for zone in data:
            _zone = self._to_zone(zone)
            zones.append(_zone)

        return zones

    def _to_zone(self, data):
        # TODO: upgrade this to v2
        id = data.get('name')
        name = data.get('name')
        extra = {
            "id": data.get("id"),
            "account_id": data.get("account_id"),
            "registrant_id": data.get("registrant_id"),
            "unicode_name": data.get("unicode_name"),
            "state": data.get("state"),
            "auto_renew": data.get("auto_renew"),
            "private_whois": data.get("private_whois"),
            "expires_on": data.get("expires_on"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at")
        }

        # All zones are primary by design
        type = 'master'

        return Zone(id=id, domain=name, type=type, ttl=DEFAULT_ZONE_TTL,
                    driver=self, extra=extra)

    def _to_records(self, data, zone):
        # TODO: upgrade this to v2
        records = []
        for item in data:
            record = self._to_record(item, zone=zone)
            records.append(record)
        return records

    def _to_record(self, data, zone_id=None, zone=None):
        # TODO: upgrade this to v2
        if not zone:  # We need zone_id or zone
            zone = self.get_zone(zone_id)
        id = data.get('id')
        name = data.get('name')
        type = data.get('type')
        content = data.get('content')
        extra = {
            "zone_id": data.get("zone_id"),
            "parent_id": data.get("parent_id"),
            "ttl": data.get("ttl"),
            "priority": data.get("priority"),
            "regions": data.get("regions"),
            "system_record": data.get("system_record"),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }
        return Record(id=id, name=name, type=type, data=content, zone=zone,
                      driver=self, ttl=data.get('ttl', None), extra=extra)
