usage = \
"""
Usage:
    changeset2route53.py <changesets> <zone> [--yaml <YAML> --spec <spec>]

Options:
    -y YAML, --yaml YAML
    -s spec, --spec spec
"""
import sys
from docopt import docopt
from r53 import *
import json

def push_changes(conn, zone_id, changes):
    changesets = [json.loads(changeset) for changeset in changes]

    rrsets = boto.route53.record.ResourceRecordSets(conn, zone_id)
    for changeset in changesets:
        record = changeset['Record']
        change = rrsets.add_change(changeset['Action'], record['Name'], record['Type'], record['TTL'])
        for resource in record['ResourceRecords']:
            change.add_value(resource['Value'])

    try:
        res = rrsets.commit()
    except Exception as e:
        print "Could not push changes: %s" % e.body
        return 1

    return 0


def main():
    args = docopt(usage)
    yaml = args['--yaml']
    if args['--spec']:
        config = get_config(yaml,args['--spec'])
    else:
        config = get_config(yaml)

    config = get_config(yaml)
    r53 = R53(config)

    changeset_file = open(args['<changesets>'], 'r')
    change_lines = changeset_file.readlines()
    zone = get_zone(r53.conn, args['<zone>'])

    push_changes(r53.conn, zone.id, change_lines)

if __name__ == '__name__':
    sys.exit(main())
