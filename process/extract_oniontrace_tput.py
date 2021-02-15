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

    net_tput = get_network_tput_per_second(data, startts, stopts)

    out = "{}/{}/oniontrace_tput.json".format(outpath, expname)
    make_directories(out)
    with open(out, 'w') as outf:
        json.dump(net_tput, outf, indent=2)

    return [True]

def get_network_tput_per_second(data, startts, stopts):
    net_tput_sec = {}
    if 'data' in data:
        for name in data['data']:
            if 'relay' not in name and '4uthority' not in name: continue

            bw = data['data'][name]['oniontrace']['bandwidth']
            key = 'bytes_written'
            if bw is None or key not in bw: continue

            tput = bw[key]

            for secstr in tput:
                sec = int(secstr)-946684800
                if sec >= startts and sec < stopts:
                    bytes = int(tput[secstr])
                    net_tput_sec.setdefault(sec, 0)
                    net_tput_sec[sec] += bytes

    return net_tput_sec

if __name__ == "__main__":
    sys.exit(main())
