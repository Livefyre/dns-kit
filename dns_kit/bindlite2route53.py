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
            print 'Error: %s' % e
            return None

    d_recs = []
    for name,rtype,value in bl_recs:
        if rtype != 'CNAME':
            continue
        if not name.endswith('.'):
            name = name + '.'
        d_rec = {'Name': name, 'TTL': '3600', 'Type': rtype}
        d_rec['ResourceRecords'] = []
        d_rec['ResourceRecords'].append({'Value': value})

        d_recs.append(d_rec)

    recs_sorted_by_name = sorted(d_recs, key=lambda k: k['Name'])
    return recs_sorted_by_name


def main():
    args = docopt(usage)
    bl = open(args['<bindlite>'], 'r')
    sorted_records = bindlite2route53(bl)

    if sorted_records:
        with safeoutput.open(args['--output']) as output:
            for record in sorted_records:
                output.write(json.dumps(record, sort_keys=True) + "\n")

        return 0
    else:
        return 1

if __name__ == '__main__':
    sys.exit(main())
