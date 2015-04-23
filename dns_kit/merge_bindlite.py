#!/usr/bin/env python

from sys import stdout, stderr
from sys import argv
from argparse import ArgumentParser
from bindlite import parse_record, sort_records
from tempfile import NamedTemporaryFile
from os.path import abspath, dirname
from os import rename

parser = ArgumentParser()
parser.add_argument('--output')
parser.add_argument('-o', '--overrides', action='store_true', help='Print the conflicts, instead of the merged zone')
parser.add_argument('-c', '--clean', action='store_true', help='Fail unless the merge applies cleanly.')
parser.add_argument('files', nargs='*', default=['/dev/stdin'], help='list of files to read. If no files are specified, reads from stdin. Files are applied in order, so last writer wins')

def bind_merge(records):
    database = {}
    conflicts = []
    for record in records:
        (name,type_,value) = record
        if (name,type_) in database:
            old_value = database[(name,type_)]
            conflicts.append( {'name':name, 'type':type_, 'old_value':old_value, 'new_value':value} )
        database[(name,type_)] = value
    return (database, conflicts)

def readDataFromFiles(fileNames):
    records = []
    for path in fileNames:
        with open(path, "r") as f:
            for line in f.readlines():
                try:
                    records.append(parse_record(line))
                except Exception as e:
                    print >>stderr, "Error in file: " + path
                    raise
    return records

def main():
    args = parser.parse_args()
    if args.output:
        out_h = NamedTemporaryFile(dir=dirname(abspath(args.output)))
    else:
        out_h = stdout
    records = readDataFromFiles(args.files)
    (merged_records, conflicts) = bind_merge(records)
    records = sort_records(records)

    if args.overrides:
        for conflict in conflicts:
            print >> stderr, "%s %s %s -> %s %s %s" % (
                    conflict['name'],
                    conflict['type'],
                    conflict['old_value'],
                    conflict['name'],
                    conflict['type'],
                    conflict['new_value'],)
    else:
        for ((name,type_),value) in merged_records.items():
            print >>out_h, name, type_, value
    if args.clean:
        if len(conflicts) == 0:
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
