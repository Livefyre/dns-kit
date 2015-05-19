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

def get_record_dicts(zone):
    database = {}
    for record in zone.get_records():
        rtype = record.type
        name = record.name.decode('unicode-escape')
        if rtype not in ('CNAME', 'A'):
            continue
        if (name,rtype) in database and 'A' == rtype:
            for value in record.resource_records:
                database[(name,rtype)]['ResourceRecords'].append(value)
        else:
            database[(name,rtype)] = {
                    'Name': name, 'TTL': record.ttl, 'Type': rtype,
                    'ResourceRecords': record.resource_records}


    recs_sorted_by_name = sorted(database.values(), key=lambda k: k['Name'])
    return recs_sorted_by_name

def main():
    args = docopt(usage)
    yaml = args['--yaml']
    if args['--spec']:
        config = get_config(yaml,args['--spec'])
    else:
        config = get_config(yaml)

    r53 = R53(config)
    zone = get_zone(r53.conn, args['<zone>'])
    records = get_record_dicts(zone)

    with safeoutput.open(args['--output']) as output:
        for record in records:
            output.write(json.dumps(record, sort_keys=True) + "\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())

