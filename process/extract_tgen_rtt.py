#!/usr/bin/env python

import os
import sys
import json
import logging

from extract_common import *

def main():
    run('tgen.analysis.json', process_tgen_rtt)

# this func is run by helper processes in process pool
def process_tgen_rtt(params):
    rootpath = params[0]
    filename = params[1]
    filepath = os.path.join(rootpath, filename)
    expname = params[2]
    outpath = params[3]

    # skip the first 20 minutes to allow the network to reach steady state
    startts, stopts = 1200, 3600

    data = load_json(filepath)

    d = get_round_trip_time(data, startts, stopts)

    out = "{}/{}/round_trip_time.json".format(outpath, expname)
    make_directories(out)
    with open(out, 'w') as outf:
        json.dump(d, outf, indent=2)

    return [True]

def get_round_trip_time(data, startts, stopts):
    rtt = []
    
    if 'data' in data:
        for name in data['data']:
            if 'perfclient' not in name: continue

            db = data['data'][name]
            ss = db['tgen']['stream_summary']

            if 'round_trip_time' in ss:
                for secstr in ss['round_trip_time']:
                    sec = int(secstr)-946684800
                    if sec >= startts and sec < stopts:
                        rtt.extend(ss['round_trip_time'][secstr])

    return rtt

if __name__ == "__main__":
    sys.exit(main())
