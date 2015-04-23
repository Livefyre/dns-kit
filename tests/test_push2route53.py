from dns_kit.push2route53 import *
from moto import mock_route53

bad_changesets = """
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "coca-cola.fyre.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "newyorker.fyre.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "wsj.fyre.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
"""

good_changesets = """
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "coca-cola.test.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "newyorker.test.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "wsj.test.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
"""

class TestPush2Route53:

    def __init__(self):
        self.conn = boto.connect_route53(
            aws_access_key_id="aws_access_key_id",
            aws_secret_access_key="aws_secret_access_key")
        self.mock = mock_route53()

    def setUp(self):
        self.mock.start()
        self.zone = self.conn.create_zone('test.co.')

    def test_get_zone(self):
        ret_zone = get_zone(self.conn, 'test.co.')
        assert isinstance(ret_zone, boto.route53.zone.Zone)
        assert ret_zone.name == 'test.co.'

    def test_push_changes(self):
        #  TODO: test error case
        #  moto doesn't throw an exception if the record name doesn't match the zone
        #  bad_changes = [bad_change.strip() for bad_change in bad_changesets.strip().split('\n')]
        #  error = push_changes(self.conn, self.zone.id, bad_changes)
        #  assert 1 == error

        good_changes = [good_change for good_change in good_changesets.strip().split('\n')]
        success = push_changes(self.conn, self.zone.id, good_changes)
        assert 0 == success

    def tearDown(self):
        self.mock.stop()
