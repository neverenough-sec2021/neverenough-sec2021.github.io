#!/usr/bin/env python

import os
import sys
import json
import logging
import datetime

from extract_common import *

def main():
    run('free.log.xz', process_free_log)

# this func is run by helper processes in process pool
def process_free_log(params):
    rootpath = params[0]
    filename = params[1]
    filepath = os.path.join(rootpath, filename)
    expname = params[2]
    outpath = params[3]

    data = load_txt(filepath)

    result = {"ram": get_ram_usage(data), "run_time": get_run_time(data)}

    out = "{}/{}/resource_usage.json".format(outpath, expname)
    make_directories(out)
    with open(out, 'w') as outf:
        json.dump(result, outf, indent=2)

    return [True]

def get_ram_usage(data):
    mem = []
    for line in data:
        if "Mem:" in line:
            parts = [p.strip() for p in line.strip().split()]
            mem.append(int(parts[2]))
    b = max(mem) - mem[0] # subtract mem used by OS
    g = b/(1024.0**3)
    return {"max_bytes_used": b, "max_gib_used": g}

def get_run_time(data):
    times = []
    for line in data:
        if "EST" in line or "EDT" in line:
            dt = datetime.datetime.strptime(line, "%a %b %d %H:%M:%S %Z %Y")
            times.append(dt)

    runtime = times[-1] - times[0]

    return {"human": str(runtime), "seconds": runtime.total_seconds()}

if __name__ == "__main__":
    sys.exit(main())
