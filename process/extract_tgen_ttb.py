#!/usr/bin/env python

import os
import sys
import json
import logging

from extract_common import *

def main():
    run('tgen.analysis.json', process_tgen_ttb)

# this func is run by helper processes in process pool
def process_tgen_ttb(params):
    rootpath = params[0]
    filename = params[1]
    filepath = os.path.join(rootpath, filename)
    expname = params[2]
    outpath = params[3]

    # skip the first 20 minutes to allow the network to reach steady state
    startts, stopts = 1200, 3600

    data = load_json(filepath)

    key = "time_to_first_byte_recv"
    d = get_file_download_time(data, startts, stopts, key)

    out = "{}/{}/{}.json".format(outpath, expname, key)
    make_directories(out)
    with open(out, 'w') as outf:
        json.dump(d, outf, indent=2)

    key = "time_to_last_byte_recv"
    d = get_file_download_time(data, startts, stopts, key)

    out = "{}/{}/{}.json".format(outpath, expname, key)
    make_directories(out)
    with open(out, 'w') as outf:
        json.dump(d, outf, indent=2)

    return [True]

def get_file_download_time(data, startts, stopts, bytekey):
    ttb = {'all':[]}
    if 'data' in data:
        for name in data['data']:
            if 'perfclient' not in name: continue
            db = data['data'][name]
            ss = db['tgen']['stream_summary']
            mybytes, mytime = 0, 0.0
            if bytekey in ss:
                for header in ss[bytekey]:
                    bytes = int(header)
                    for secstr in ss[bytekey][header]:
                        sec = int(secstr)-946684800
                        if sec >= startts and sec < stopts:
                            #mydlcount += len(data['nodes'][name]['lastbyte'][header][secstr])
                            for dl in ss[bytekey][header][secstr]:
                                seconds = float(dl)
                                ttb['all'].append(seconds)
                                ttb.setdefault(header, []).append(seconds)
    return ttb

if __name__ == "__main__":
    sys.exit(main())
