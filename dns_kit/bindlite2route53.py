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
from r53 import *

def bindlite2route53(bl_file):

    def group_bls(bls):
        group_func = lambda (name, rtype, value): (name,rtype)
        for k, g in itertools.groupby(bls,key=group_func):
            yield (k,[val for n,t,val in g])

    bl_recs = []
    for line in bl_file.readlines():
        try:
            bl_recs.append(parse_record(line))
        except ValueError as e:
            sys.exit('Error: %s' % e)

    r53s = []
    for (name,rtype),values in group_bls(bl_recs):
        try:
            r53s.append(r53_record(name,rtype,values))
        except ValueError as e:
            continue

    recs_sorted_by_name = sorted(r53s, key=lambda k: k['Name'])
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
