from dns_kit.route53dump import *
from moto import mock_route53

class TestR53Dump:

    def __init__(self):
        self.conn = boto.connect_route53(
            aws_access_key_id="aws_access_key_id",
            aws_secret_access_key="aws_secret_access_key")
        self.mock = mock_route53()
    
    def setUp(self):
        self.mock.start()
        self.zone = self.conn.create_zone('test.co.')
        self.zone.add_cname('test.test.co.','www.livefyre.com',300)
        self.zone.add_a('arecord.test.co.','1.2.3.4',300)

    def test_get_zone(self):
        ret_zone = get_zone(self.conn, 'test.co.')
        assert isinstance(ret_zone, boto.route53.zone.Zone)
        assert ret_zone.name == 'test.co.'

    def test_get_record_dicts(self):
        ret_zone = get_zone(self.conn, 'test.co.')
        recs = get_record_dicts(ret_zone)
        assert {'Name':'test.test.co.','ResourceRecords':['www.livefyre.com.'],'TTL':'300','Type':'CNAME'} in recs
        assert {'Name':'arecord.test.co.','ResourceRecords':['1.2.3.4'],'TTL':'300','Type':'A'} in recs

    def tearDown(self):
        self.zone.delete()
        self.mock.stop()
