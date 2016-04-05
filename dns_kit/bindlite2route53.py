usage = \
"""
Usage:
    bindlite2route53.py <bindlite> [--zone <zone>] [--output <output>]

Options:
    -o output, --output output
    -z zone, --zone zone
"""
import sys
from docopt import docopt
from bindlite import parse_record
import json
import safeoutput
from r53 import *

def bindlite2route53(bl_file, zone):

    def fqdnify_bl(zone, bl):
        (name, type, value) = bl
        if zone:
          name = '.'.join([name, zone])
        return (name, type, value)

    def group_bls(bls):
        group_func = lambda (name, rtype, value): (name,rtype)
        for k, g in itertools.groupby(bls,key=group_func):
            yield (k,[val for n,t,val in g])

    bl_recs = [parse_record(line) for line in bl_file.readlines()]
    # BindLite uses non-fully qualified names. Route53 expects fully qualified names.
    fqdn_recs = [fqdnify_bl(zone, x) for x in bl_recs]
    r53s = [r53_record(name,rtype,values) for (name,rtype),values in group_bls(fqdn_recs)]

    recs_sorted_by_name = sorted(r53s, key=lambda k: k['Name'])
    return recs_sorted_by_name


def main():
    args = docopt(usage)
    bl = open(args['<bindlite>'], 'r')
    sorted_records = bindlite2route53(bl, args['--zone'])

    with safeoutput.open(args['--output']) as output:
        for record in sorted_records:
            output.write(json.dumps(record, sort_keys=True) + "\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())
