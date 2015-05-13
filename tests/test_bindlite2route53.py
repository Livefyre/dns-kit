from nose.tools import assert_raises
from dns_kit.bindlite2route53 import *
from moto import mock_route53
from StringIO import StringIO

bad_bindlites = """
macadamianuts.fyre.co.     CNAMEwww.livefyre.com
nicho.fyre.co.      CNAME www.livefyre.com
noearzcat.fyre.co.CNAME    www.livefyre.com
"""

good_bindlites = """
macadamianuts.fyre.co. CNAME www.livefyre.com
nicho.fyre.co. CNAME www.livefyre.com
noearzcat.fyre.co. CNAME www.livefyre.com
"""

good_r53 = [{'ResourceRecords': [{'Value': 'www.livefyre.com'}], 'Type': 'CNAME', 'Name': 'macadamianuts.fyre.co.', 'TTL': '3600'}, {'ResourceRecords': [{'Value': 'www.livefyre.com'}], 'Type': 'CNAME', 'Name': 'nicho.fyre.co.', 'TTL': '3600'}, {'ResourceRecords': [{'Value': 'www.livefyre.com'}], 'Type': 'CNAME', 'Name': 'noearzcat.fyre.co.', 'TTL': '3600'}]

class TestBindlite2Route53():

    def setUp(self):
        self.good_file = StringIO(good_bindlites.strip())
        self.bad_file = StringIO(bad_bindlites.strip())

    def test_bindlite2route53(self):
        good_records = bindlite2route53(self.good_file)
        assert isinstance(good_records, list)
        assert good_r53 == good_records

        assert_raises(SystemExit, bindlite2route53, self.bad_file)

    def tearDown(self):
        self.good_file.close()
        self.bad_file.close()

