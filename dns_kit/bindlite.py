#!/usr/bin/env python

import re

record_pattern = re.compile("^(?P<name>[^ ]+) (?P<type>[^ ]+) (?P<value>.*)$")

def parse_record(line):
    match = record_pattern.match(line)
    if not match:
        raise ValueError("%s is not a record" %(line))
    name_type_value = match.groups()
    return name_type_value

def sort_records(records):
    return sorted(records, cmp=cmp_record)

def cmp_record(x,y):
    x = (x[1], x[0], x[2])
    y = (y[1], y[0], y[2])
    # print x,y, cmp(x,y)
    return cmp(x, y)


