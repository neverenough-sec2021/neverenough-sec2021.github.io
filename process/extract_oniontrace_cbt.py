#!/usr/bin/env python

import os
import sys
import json
import logging

from extract_common import *

def main():
    run('oniontrace.analysis.json', process_oniontrace_tput)

# this func is run by helper processes in process pool
def process_oniontrace_tput(params):
    rootpath = params[0]
    filename = params[1]
    filepath = os.path.join(rootpath, filename)
    expname = params[2]
    outpath = params[3]

    # skip the first 20 minutes to allow the network to reach steady state
    startts, stopts = 1200, 3600

    data = load_json(filepath)

    cbts = get_perfclient_cbt(data, startts, stopts)

    out = "{}/{}/oniontrace_perfclient_cbt.json".format(outpath, expname)
    make_directories(out)
    with open(out, 'w') as outf:
        json.dump(cbts, outf, indent=2)

    return [True]

def get_perfclient_cbt(data, startts, stopts):
    perf_cbt = {}
    if 'data' in data:
        for name in data['data']:
            if 'perfclient' not in name: continue

            circ = data['data'][name]['oniontrace']['circuit']
            key = 'build_time'
            if circ is None or key not in circ: continue

            cbt = circ[key]

            for secstr in cbt:
                sec = int(secstr)-946684800
                if sec >= startts and sec < stopts:
                    perf_cbt.setdefault(sec, [])
                    perf_cbt[sec].extend(cbt[secstr])

    return perf_cbt

if __name__ == "__main__":
    sys.exit(main())
