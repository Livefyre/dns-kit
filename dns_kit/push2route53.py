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
import itertools


#  group CREATEs and DELETEs of same record together
def group_and_batch(changes, batch_size=1000, group_func=lambda x: x['Record']['Name']):
    sorted_changes = sorted(changes, key=group_func)
    grouped_changes = [list(g) for k, g, in itertools.groupby(sorted_changes, key=group_func)]

    changesets = []
    this_changeset = []
    for group in grouped_changes:
        #  DELETEs before CREATEs
        sorted_group = sorted(group, key=lambda change: change['Action'], reverse=True)
        for ndx, change in enumerate(sorted_group):
            if ndx + len(this_changeset) < batch_size:
                this_changeset.append(change)
            else:
                changesets.append(this_changeset)
                this_changeset = [change]

    changesets.append(this_changeset)
    return changesets


def push_changes(conn, zone_id, changelist):

    changes = [json.loads(change) for change in changelist]

    changesets = group_and_batch(changes, 1000, lambda x: x['Record']['Name'])

    for index, changeset in enumerate(changesets):
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
