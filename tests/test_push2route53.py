from nose.tools import assert_raises
from dns_kit.push2route53 import *
from moto import mock_route53

class inputstr(str):
    def readlines(self):
        return self.strip().split('\n')

bad_changeset = inputstr("""
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "coca-cola.fyre.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "newyorker.fyre.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "newyorker.fyre.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "wsj.fyre.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "newyorker.fyre.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
""")

good_changeset = inputstr("""
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "newyorker.test.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "wsj.test.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "coca-cola.test.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "DELETE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "newyorker.test.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
{"Action": "CREATE", "Record": {"TTL": "3600", "Type": "CNAME", "Name": "si.test.co.", "ResourceRecords": [{"Value": "www.livefyre.com"}]}}
""")

class TestPush2Route53:

    def __init__(self):
        self.conn = boto.connect_route53(
            aws_access_key_id="aws_access_key_id",
            aws_secret_access_key="aws_secret_access_key")
        self.mock = mock_route53()

    def setUp(self):
        self.mock.start()
        self.zone = self.conn.create_zone('test.co.')
        self.good_changes = [json.loads(good_change) for good_change in good_changeset.strip().split('\n')]
        self.bad_changes = [json.loads(good_change) for good_change in bad_changeset.strip().split('\n')]

    def test_get_zone(self):
        ret_zone = self.conn.get_zone('test.co.')
        assert isinstance(ret_zone, boto.route53.zone.Zone)
        assert ret_zone.name == 'test.co.'

    def test_parse_changes(self):
        changes = parse_changes(good_changeset)
        assert changes == self.good_changes

        bad_changes = parse_changes(bad_changeset)
        assert bad_changes == self.bad_changes

    def test_push_changes(self):
        success = push_changes(self.conn, self.zone.id, self.good_changes)
        assert 0 == success

        #  TODO: test error case
        #  moto doesn't throw an exception if the record name doesn't match the zone
        #  bad_changes = [bad_change.strip() for bad_change in bad_changeset.strip().split('\n')]
        #  error = push_changes(self.conn, self.zone.id, bad_changes)
        #  assert 1 == error

    def test_group_changes_by(self):
        name_groups = group_changes_by(self.good_changes, lambda change: change['Record']['Name'])

        # it sorts by record name
        flattened = [change for group in name_groups for change in group]
        assert all(flattened[i]['Record']['Name'] <= flattened[i+1]['Record']['Name'] for i in xrange(len(flattened)-1))

        # it groups records by name
        names = []
        for group in name_groups:
            assert all(len(set([x['Record']['Name']])) == 1 for x in group)
            names.append(set([x['Record']['Name'] for x in group]))
        assert not set.intersection(*names)

    def test_batch_changes(self):
        name_groups = group_changes_by(self.good_changes)
        changesets = batch_changes(name_groups, 2)

        # it returns batches no greater than specified
        assert all(len(batch) <= 2 for batch in changesets)

        # it will not split records with the same name between batches
        names_by_batch = [set([change['Record']['Name'] for change in batch]) for batch in changesets]
        assert not set.intersection(*names_by_batch)

        # it raises a ValueError if the size of a change group is greater than the batch size
        bad_name_groups = group_changes_by(self.bad_changes)
        assert_raises(ValueError,
            batch_changes, bad_name_groups, 2)


    def tearDown(self):
        self.mock.stop()
