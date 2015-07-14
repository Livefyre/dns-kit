usage = \
"""
Usage:
    bindlite_lookup.py <bl> [--output=<output> --workers=<workers>]

Options:
    -o output, --output output     Output file name
    -w workers, --workers workers  Number of workers [default: 5].
"""
from docopt import docopt
from bindlite import parse_record
import safeoutput

import time
import sys, os
import subprocess
import errno

dev_null = open("/dev/null", "rw")
def check_host(record):
    proc = subprocess.Popen(["host", record.strip()], stdin=dev_null, stdout=dev_null)
    return proc.pid, proc

def run(pool, todos):

    jobs = {}
    while todos or jobs:
        while todos and len(jobs) < pool:
            record = todos.pop(0)
            (pid, proc) = check_host(record[0])
            jobs[pid] = (record, proc)

        try:
            pid, ret_code = os.wait()
        except OSError as e:
            if e.errno != errno.ECHILD:
                raise
        else:
            (record, proc) = jobs.pop(pid)
            yield (record, ret_code)

def main():
    args = docopt(usage)
    records = []
    with open(args['<bl>']) as bl:
        for line in bl.readlines():
            record = parse_record(line)
            if record[1] in ('CNAME', 'A'):
                records.append(record)

    workers = int(args['--workers'])

    with safeoutput.open(args['--output']) as output:
        for record, ret_code in run(workers, records):
            sys.stderr.write("%s,\t\t%d\n" % (" ".join(record), ret_code))
            if ret_code != 0:
                output.write("%s\n" % " ".join(record))

if __name__ == '__main__':
    main()

    sys.exit(0)

