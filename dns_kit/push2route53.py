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


def group_changes_by(changes, group_func=lambda x: x['Record']['Name']):
    sorted_changes = sorted(changes, key=group_func)
    grouped_changes = [list(g) for k, g, in itertools.groupby(sorted_changes, key=group_func)]

    return grouped_changes

def batch_changes(change_groups, batch_size=1000):
    changesets = []
    this_changeset = []
    for group in change_groups:
        #  DELETEs before CREATEs
        sorted_group = sorted(group, key=lambda change: change['Action'], reverse=True)
        if len(this_changeset) + len(group) <= batch_size:
            [this_changeset.append(change) for change in sorted_group]
        else:
            changesets.append(this_changeset)
            if len(group) <= batch_size:
                this_changeset = sorted_group
            else:
                raise ValueError("Number of grouped records greater than batch size")

    changesets.append(this_changeset)
    return changesets


def push_changes(conn, zone_id, changes):

    # group CREATEs and DELETEs of same record together
    grouped_by_name = group_changes_by(changes, lambda change: change['Record']['Name'])
    # create batches of 1000 or less
    changesets = batch_changes(grouped_by_name, 1000)

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
    changes = [json.loads(change) for change in change_lines]

    push_changes(r53.conn, zone.id, change_lines)

if __name__ == '__main__':
    sys.exit(main())
