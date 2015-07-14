import os
import sys
from pyyacc import parser
import boto.route53
from boto.route53 import Route53Connection
import itertools

class R53(object):
    def __init__(self, config):
        self.config = config
        self.conn = Route53Connection(
            config['dns_kit']['aws_access_key'],
            config['dns_kit']['aws_secret_key'])

def get_config(yaml, spec=None):
    if not yaml:
        print 'config required'
        sys.exit(1)

    if not spec:
        spec = os.path.join(os.path.dirname(__file__), './app.yaml')

    builder, config = parser.build(spec, yaml)
    validate = builder.validate(config)
    if validate:
        sys.stderr.write(
            'insufficient config, missing:\n' +
            '\n'.join([(4*' ')+':'.join(x) for x in validate.iterkeys()]) +
            '\n')
        sys.exit(1)

    return config

def r53_record(name, rtype, resources, ttl='3600'):
    if rtype not in ('CNAME','A'):
        raise ValueError('not a CNAME or A record')
    if not name.endswith('.'):
        name += '.'
    return {'Name':name, 'TTL':ttl, 'Type':rtype,'ResourceRecords':resources}


# monkey patch Route53Connection.make_request with short sleep
# because API rate limiting
old_request_method = Route53Connection.make_request
def make_gentle_request(self, action, path, headers=None, data='', params=None):
      import time; time.sleep(0.2)
      res = old_request_method(self, action, path, headers, data, params)
      return res

Route53Connection.make_request = make_gentle_request

