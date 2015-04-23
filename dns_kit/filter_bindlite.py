#!/usr/bin/env python

from sys import stdout, stderr
from argparse import ArgumentParser
from bindlite import parse_record, sort_records
from tempfile import NamedTemporaryFile
from os.path import abspath, dirname
from os import rename

parser = ArgumentParser()
parser.add_argument('-o', '--output')
parser.add_argument('-r', '--removals', action='store_true', help='Print the removed records, instead of the resulting zone')
parser.add_argument('-c', '--clean', action='store_true', help='Fail unless the input zone has no blacklist entries.')
parser.add_argument('-b', '--blacklist', required=True, help='blacklist file')
parser.add_argument('files', nargs='*', default=['/dev/stdin'], help='list of files to read. If no files are specified, reads from stdin. Files are applied in order, so last writer wins')

def bind_filter(records, blacklist):
    remaining = []
    removals = []
    for record in records:
        if record in blacklist:
            removals.append(record)
        else:
            remaining.append(record)
    return (remaining, removals)


def import_records(paths):
    records = []
    for path in paths:
        with open(path, "r") as f:
            for line in f.readlines():
                try:
                    records.append(parse_record(line))
                except Exception as e:
                    # print "Working on file: " + host_file #TODO Make part of exception message.
                    raise
    return records

def main():
    args = parser.parse_args()
    if args.output:
        out_h = NamedTemporaryFile(dir=dirname(abspath(args.output)))
    else:
        out_h = stdout

    blacklist = import_records([args.blacklist])
    records = import_records(args.files)

    (remaining, removals) = bind_filter(records, blacklist)

    remaining = sort_records(remaining)
    removals = sort_records(removals)

    if args.removals:
        for removal in removals:
            (name,type,value) = removal
            print >> stderr, name, type, value
    else:
        for (name,type,value) in remaining:
            print >>out_h, name, type, value
    if args.clean:
        if len(removals) == 0:
            if args.output:
                rename(out_h.name, args.output)
                out_h.delete = False
            exit(0)
        else:
            exit(1)
    else:
        if args.output:
            rename(out_h.name, args.output)
            out_h.delete = False
        exit(0)

if __name__ == "__main__":
    main()

