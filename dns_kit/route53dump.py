usage = \
"""
Usage:
    route53dump.py <zone> [--yaml <YAML> --spec <spec> --output <output>]

Options:
    -y YAML, --yaml YAML
    -s spec, --spec spec
    -o output, --output output
"""
import sys
from docopt import docopt
from r53 import *
import json
import safeoutput

def get_r53_records(zone):
    r53s = []
    for record in zone.get_records():
        rtype = record.type
        name = record.name.decode('unicode-escape')
        values = record.resource_records
        try:
            r53s.append(r53_record(name,rtype,values,record.ttl))
        except ValueError as e:
            continue

    recs_sorted_by_name = sorted(r53s, key=lambda k: k['Name'])
    return recs_sorted_by_name

def main():
    args = docopt(usage)
    yaml = args['--yaml']
    if args['--spec']:
        config = get_config(yaml,args['--spec'])
    else:
        config = get_config(yaml)

    r53 = R53(config)
    zone = r53.conn.get_zone(args['<zone>'])
    records = get_r53_records(zone)

    with safeoutput.open(args['--output']) as output:
        for record in records:
            output.write(json.dumps(record, sort_keys=True) + "\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())

