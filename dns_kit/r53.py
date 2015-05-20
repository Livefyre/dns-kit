import os
import sys
from pyyacc import parser
import boto.route53
import itertools

class R53(object):
    def __init__(self, config):
        self.config = config
        self.conn = boto.route53.connection.Route53Connection(
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

def get_zone(conn, name):
    zone = conn.get_zone(name)
    return zone

def r53_record(name, rtype, resources, ttl='3600'):
    if rtype not in ('CNAME','A'):
        raise ValueError('not a CNAME or A record')
    if not name.endswith('.'):
        name += '.'
    return {'Name':name, 'TTL':ttl, 'Type':rtype,'ResourceRecords':resources}

