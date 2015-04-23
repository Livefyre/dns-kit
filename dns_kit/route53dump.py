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
    rec_dicts = []

    #TODO make more general purpose (rm CNAME specific stuff)
    for record in zone.get_records():
        if record.type != 'CNAME':
            continue
        rec_dict = {'Name': record.name, 'TTL': record.ttl, 'Type': record.type}
        rec_dict['ResourceRecords'] = []
        for value in record.resource_records:
            rec_dict['ResourceRecords'].append( {'Value': value} )

        rec_dicts.append(rec_dict)

    recs_sorted_by_name = sorted(rec_dicts, key=lambda k: k['Name'])
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

