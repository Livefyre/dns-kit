usage = \
"""
Usage:
    bindlite2route53.py <bindlite> [--output <output>]

Options:
    -o output, --output output
"""
import sys
from docopt import docopt
from bindlite import parse_record
import json
import safeoutput

def bindlite2route53(bl_file):
    bl_recs = []
    for line in bl_file.readlines():
        try:
            bl_recs.append(parse_record(line))
        except ValueError as e:
            sys.exit('Error: %s' % e)

    database = {}
    for name,rtype,value in bl_recs:
        if rtype not in ('CNAME', 'A'):
            continue
        if not name.endswith('.'):
            name = name + '.'
        if (name,rtype) in database and 'A' == rtype:
            database[(name,rtype)]['ResourceRecords'].append(value)
        else:
            database[(name,rtype)] = {
                    'Name': name, 'TTL': '3600', 'Type': rtype,
                    'ResourceRecords':[value]}

    recs_sorted_by_name = sorted(database.values(), key=lambda k: k['Name'])
    return recs_sorted_by_name


def main():
    args = docopt(usage)
    bl = open(args['<bindlite>'], 'r')
    sorted_records = bindlite2route53(bl)

    with safeoutput.open(args['--output']) as output:
        for record in sorted_records:
            output.write(json.dumps(record, sort_keys=True) + "\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())
