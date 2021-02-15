#!/usr/bin/env python

import os
import sys
import json
import logging

from extract_common import *

def main():
    run('tgen.analysis.json', process_tgen_errrate)

# this func is run by helper processes in process pool
def process_tgen_errrate(params):
    rootpath = params[0]
    filename = params[1]
    filepath = os.path.join(rootpath, filename)
    expname = params[2]
    outpath = params[3]

    # skip the first 20 minutes to allow the network to reach steady state
    startts, stopts = 1200, 3600

    data = load_json(filepath)

    errrate_per_client = get_error_rate(data, startts, stopts)

    out = "{}/{}/error_rate.json".format(outpath, expname)
    make_directories(out)
    with open(out, 'w') as outf:
        json.dump(errrate_per_client, outf, indent=2)

    return [True]

def get_error_rate(data, startts, stopts):
    errors_per_client = {'ALL': []}
    if 'data' in data:
        for name in data['data']:
            if 'perfclient' not in name: continue
            db = data['data'][name]
            ss = db['tgen']['stream_summary']

            mydlcount = 0
            errtype_counts = {'ALL': 0}

            key = 'time_to_last_byte_recv'
            if key in ss:
                for header in ss[key]:
                    for secstr in ss[key][header]:
                        sec = int(secstr)-946684800
                        if sec >= startts and sec < stopts:
                            mydlcount += len(ss[key][header][secstr])

            key = 'errors'
            if key in ss:
                for errtype in ss[key]:
                    for secstr in ss[key][errtype]:
                        sec = int(secstr)-946684800
                        if sec >= startts and sec < stopts:
                            num_err = len(ss[key][errtype][secstr])
                            errtype_counts.setdefault(errtype, 0)
                            errtype_counts[errtype] += num_err
                            errtype_counts['ALL'] += num_err

            attempted_dl_count = mydlcount+errtype_counts['ALL']

            #logging.info("attempted {} downloads, {} completed, {} failed".format(attempted_dl_count, mydlcount, errtype_counts['ALL']))

            if attempted_dl_count > 0:
                errcount = float(errtype_counts['ALL'])
                dlcount = float(attempted_dl_count)

                error_rate = 100.0*errcount/dlcount
                resolution = 100.0/dlcount
                errors_per_client['ALL'].append([error_rate, resolution])

                for errtype in errtype_counts:
                    errcount = float(errtype_counts[errtype])
                    error_rate = 100.0*errcount/dlcount
                    resolution = 100.0/dlcount
                    errors_per_client.setdefault(errtype, []).append([error_rate, resolution])

    return errors_per_client

if __name__ == "__main__":
    sys.exit(main())
