usage = \
"""
Usage:
    push2route53.py <changesets> <zone> [--yaml <YAML> --spec <spec>]

Options:
    -y YAML, --yaml YAML
    -s spec, --spec spec
"""
import sys
from docopt import docopt
from r53 import *
import json
import itertools

def parse_changes(changefile):
    change_lines = changefile.readlines()
    changes = [json.loads(change) for change in change_lines]
    return changes

def group_changes_by(changes, group_func=lambda x: x['Record']['Name']):
    sorted_changes = sorted(changes, key=group_func)
    grouped_changes = [list(g) for k, g, in itertools.groupby(sorted_changes, key=group_func)]

    return grouped_changes

def batch_changes(change_groups, batch_size=1000):
    batches = []
    this_batch = []
    batch_rec_length = 0
    for group in change_groups:
        grp_rec_length = sum([len(change['Record']['ResourceRecords']) for change in group])
        #  DELETEs before CREATEs
        sorted_group = sorted(group, key=lambda change: change['Action'], reverse=True)
        if batch_rec_length + grp_rec_length <= batch_size:
            [this_batch.append(change) for change in sorted_group]
            batch_rec_length += grp_rec_length
        else:
            batches.append(this_batch)
            if grp_rec_length <= batch_size:
                this_batch = sorted_group
                batch_rec_length = grp_rec_length
            else:
                raise ValueError("Number of grouped records greater than batch size")

    batches.append(this_batch)
    return batches


def push_changes(conn, zone_id, changes):

    # group CREATEs and DELETEs of same record together
    grouped_by_name = group_changes_by(changes, lambda change: change['Record']['Name'])
    # create batches of 1000 or less
    batches = batch_changes(grouped_by_name, 1000)

    for index, batch in enumerate(batches):
        rrsets = boto.route53.record.ResourceRecordSets(conn, zone_id)
        for change in batch:
            record = change['Record']
            rrset_change = rrsets.add_change(change['Action'], record['Name'], record['Type'], record['TTL'])
            for resource in record['ResourceRecords']:
                rrset_change.add_value(resource)

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

    r53 = R53(config)
    zone = r53.conn.get_zone(args['<zone>'])

    change_file = open(args['<changesets>'], 'r')
    changes = parse_changes(change_file)
    push_changes(r53.conn, zone.id, changes)

if __name__ == '__main__':
    sys.exit(main())
