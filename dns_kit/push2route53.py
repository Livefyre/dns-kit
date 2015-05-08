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

def push_changes(conn, zone_id, changelist):
    changes = [json.loads(change) for change in changelist]
    sorted_changes = sorted(changes, key=lambda change: change['Record']['Name'])

    total_changes = len(sorted_changes)
    changesets = []

    import pdb; pdb.set_trace()
    i = 0
    while i < total_changes:
        # limit per push of 1000 records
        if i + 1000 < total_changes:
            # we don't want a pair of changes for the same record to be in separate pushes
            if sorted_changes[i+999]['Record']['Name'] == sorted_changes[i+1000]['Record']['Name']:
                range_end = i + 999
            else:
                range_end = i + 1000
        else:
            range_end = total_changes

        changesets.append(sorted_changes[i:range_end])
        i = range_end

    for changeset in changesets:
        import pdb; pdb.set_trace()
        rrsets = boto.route53.record.ResourceRecordSets(conn, zone_id)
        for change in changeset:
            record = change['Record']
            rrset_change = rrsets.add_change(change['Action'], record['Name'], record['Type'], record['TTL'])
            for resource in record['ResourceRecords']:
                rrset_change.add_value(resource['Value'])

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

if __name__ == '__main__':
    sys.exit(main())
