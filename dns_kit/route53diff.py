usage = \
"""
Usage:
    route53diff.py <current> <desired> [--output <output>]

Options:
    -o output, --output output
"""
import sys
from docopt import docopt
import difflib
import json
import safeoutput

def stamp_change(records, change):
    for line in records:
        record_dict = json.loads(line)
        change_dict = {'Action': change, 'Record': record_dict}
        yield json.dumps(change_dict) + "\n"

def sort_resource_records(r53_file):
    sorted_output = []
    for obj in r53_file.readlines():
        _dict = json.loads(obj)
        _dict['ResourceRecords'] = sorted(_dict['ResourceRecords'])
        sorted_output.append(json.dumps(_dict))

    return sorted_output


def main():
    args = docopt(usage)
    current_file = open(args['<current>'], 'r')
    desired_file = open(args['<desired>'], 'r')


    # assumes input files are ordered
    delta = difflib.ndiff(sort_resource_records(current_file),
                sort_resource_records(desired_file))

    delta = list(delta)
    to_delete = [line.replace('- ','') for line in delta if line.startswith('-')]
    to_create = [line.replace('+ ','') for line in delta if line.startswith('+')]

    to_delete = stamp_change(to_delete, 'DELETE')
    to_create = stamp_change(to_create, 'CREATE')

    changes = list(to_delete) + list(to_create)

    with safeoutput.open(args['--output']) as output:
        output.writelines(changes)

    return 0


if __name__ == '__main__':
    sys.exit(main())
